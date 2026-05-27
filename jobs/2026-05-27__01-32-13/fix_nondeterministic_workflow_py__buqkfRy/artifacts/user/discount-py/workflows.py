import datetime

from temporalio import workflow

from activities import pick_discount


@workflow.defn(name="DiscountWorkflow")
class DiscountWorkflow:
    @workflow.run
    async def run(self, user_id: str) -> dict:
        now = workflow.now()
        discount = await workflow.execute_activity(
            pick_discount,
            start_to_close_timeout=datetime.timedelta(seconds=10),
        )
        return {
            "user_id": user_id,
            "discount": discount,
            "decided_at": now.isoformat(),
        }
