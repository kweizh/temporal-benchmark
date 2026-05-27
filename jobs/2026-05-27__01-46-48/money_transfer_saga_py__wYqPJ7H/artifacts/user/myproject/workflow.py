"""
Temporal workflow for the Money Transfer Saga.
"""
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError, ApplicationError

with workflow.unsafe.imports_passed_through():
    from activities import deposit, refund, withdraw

# Retry policy used for all activities: no automatic retries so a failure is
# reported immediately to the workflow (deposit already raises non-retryable,
# but being explicit here is cleaner).
_NO_RETRY = RetryPolicy(maximum_attempts=1)


@workflow.defn
class MoneyTransferWorkflow:
    @workflow.run
    async def run(self, from_account: str, to_account: str, amount: int) -> str:
        workflow.logger.info(
            "Starting transfer: %s -> %s, amount=%d",
            from_account,
            to_account,
            amount,
        )

        # Step 1: Withdraw
        await workflow.execute_activity(
            withdraw,
            args=[from_account, amount],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=_NO_RETRY,
        )

        # Step 2: Deposit — compensate with refund on failure
        try:
            await workflow.execute_activity(
                deposit,
                args=[to_account, amount],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=_NO_RETRY,
            )
        except ActivityError as exc:
            workflow.logger.warning(
                "Deposit to %s failed (%s); running refund compensation",
                to_account,
                exc,
            )
            # Compensation: put the money back
            await workflow.execute_activity(
                refund,
                args=[from_account, amount],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=_NO_RETRY,
            )
            # Re-raise so the workflow ends in FAILED state
            raise ApplicationError(
                f"Transfer {from_account} -> {to_account} failed after refund compensation",
                non_retryable=True,
            ) from exc

        workflow.logger.info(
            "Transfer complete: %s -> %s, amount=%d",
            from_account,
            to_account,
            amount,
        )
        return f"transferred {amount} from {from_account} to {to_account}"
