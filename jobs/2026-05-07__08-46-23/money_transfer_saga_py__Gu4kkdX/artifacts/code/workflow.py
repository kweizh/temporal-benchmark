from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activity definitions for type hinting
with workflow.unsafe.imports_passed_through():
    from activities import withdraw, deposit, refund

@workflow.defn
class MoneyTransferSaga:
    @workflow.run
    async def run(self, source_account: str, target_account: str, amount: int) -> None:
        # Step 1: Withdraw
        await workflow.execute_activity(
            withdraw,
            args=[source_account, amount],
            start_to_close_timeout=timedelta(seconds=5),
        )

        try:
            # Step 2: Deposit
            await workflow.execute_activity(
                deposit,
                args=[target_account, amount],
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(maximum_attempts=1), # Fail fast for this demo if it's B_FAIL
            )
        except Exception as e:
            # Step 3: Compensation - Refund
            await workflow.execute_activity(
                refund,
                args=[source_account, amount],
                start_to_close_timeout=timedelta(seconds=5),
            )
            raise e
