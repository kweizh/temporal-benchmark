from datetime import timedelta
from temporalio import workflow

# Import activity type hint if needed, but we can use string name for execute_activity
# to avoid circular imports if we were being super careful, 
# but here it's fine to just use the name "pick_discount".

@workflow.defn(name="DiscountWorkflow")
class DiscountWorkflow:
    @workflow.run
    async def run(self, user_id: str) -> dict:
        # Use Temporal's deterministic time API
        now = workflow.now()
        
        # Call the activity for randomness
        discount = await workflow.execute_activity(
            "pick_discount",
            start_to_close_timeout=timedelta(seconds=5)
        )
        
        return {
            "user_id": user_id,
            "discount": discount,
            "decided_at": now.isoformat(),
        }
