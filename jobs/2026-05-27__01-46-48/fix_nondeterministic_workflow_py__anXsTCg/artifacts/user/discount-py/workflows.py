import datetime
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import pick_discount


@workflow.defn(name="DiscountWorkflow")
class DiscountWorkflow:
    @workflow.run
    async def run(self, user_id: str) -> dict:
        # Use Temporal's deterministic time API (workflow.now()) for determinism
        now: datetime.datetime = workflow.now()

        # Delegate randomness to an Activity so the Workflow stays deterministic
        discount: int = await workflow.execute_activity(
            pick_discount,
            start_to_close_timeout=datetime.timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        return {
            "user_id": user_id,
            "discount": discount,
            "decided_at": now.isoformat(),
        }
