from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import notify

@workflow.defn
class ReminderWorkflow:
    @workflow.run
    async def run(self, duration: int, message: str) -> str:
        await workflow.sleep(timedelta(seconds=duration))
        return await workflow.execute_activity(
            notify,
            message,
            start_to_close_timeout=timedelta(seconds=5),
        )
