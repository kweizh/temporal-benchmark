from datetime import timedelta
from temporalio import workflow
import asyncio

# Import activity type for type hinting
with workflow.unsafe.imports_passed_through():
    from activities import notify

@workflow.def
class ReminderWorkflow:
    @workflow.run
    async def run(self, message: str, delay_seconds: int) -> str:
        # Durable timer
        await asyncio.sleep(delay_seconds)
        
        # Execute activity
        return await workflow.execute_activity(
            notify,
            message,
            start_to_close_timeout=timedelta(seconds=10)
        )
