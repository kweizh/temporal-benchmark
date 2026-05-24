from datetime import timedelta
from temporalio import workflow

# Import activity, pull it in via string name to avoid circular imports if needed, 
# but here we can just import it.
with workflow.unsafe.imports_passed_through():
    from activities import greet

@workflow.defn
class HelloWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            greet,
            name,
            start_to_close_timeout=timedelta(seconds=5),
        )
