from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import old_activity, new_activity

@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self) -> str:
        if workflow.patched("use_new_activity"):
            return await workflow.execute_activity(
                new_activity,
                start_to_close_timeout=timedelta(seconds=5),
            )
        else:
            return await workflow.execute_activity(
                old_activity,
                start_to_close_timeout=timedelta(seconds=5),
            )
