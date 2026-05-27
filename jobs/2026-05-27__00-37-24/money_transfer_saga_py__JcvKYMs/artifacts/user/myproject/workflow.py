from datetime import timedelta
from temporalio import workflow
from temporalio.exceptions import ActivityError, ApplicationError

with workflow.unsafe.imports_passed_through():
    from activities import withdraw, deposit, refund

@workflow.defn
class MoneyTransferWorkflow:
    @workflow.run
    async def run(self, from_account: str, to_account: str, amount: int) -> str:
        # Step 1: Withdraw
        await workflow.execute_activity(
            withdraw,
            args=[from_account, amount],
            start_to_close_timeout=timedelta(seconds=5),
        )

        # Step 2: Deposit
        try:
            await workflow.execute_activity(
                deposit,
                args=[to_account, amount],
                start_to_close_timeout=timedelta(seconds=5),
            )
        except ActivityError as e:
            # Step 3: Refund if deposit fails
            await workflow.execute_activity(
                refund,
                args=[from_account, amount],
                start_to_close_timeout=timedelta(seconds=5),
            )
            raise ApplicationError(f"Transfer failed: {str(e)}") from e

        return f"Transfer of {amount} from {from_account} to {to_account} completed successfully"
