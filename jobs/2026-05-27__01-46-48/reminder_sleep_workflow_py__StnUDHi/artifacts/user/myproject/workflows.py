import asyncio
from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import notify


@workflow.defn(name="ReminderWorkflow")
class ReminderWorkflow:
    @workflow.run
    async def run(self, message: str, delay_seconds: int) -> str:
        # Durable timer: Temporal converts asyncio.sleep into a server-side timer
        # that survives worker restarts.
        await asyncio.sleep(delay_seconds)

        result = await workflow.execute_activity(
            notify,
            message,
            start_to_close_timeout=timedelta(seconds=30),
        )
        return result
