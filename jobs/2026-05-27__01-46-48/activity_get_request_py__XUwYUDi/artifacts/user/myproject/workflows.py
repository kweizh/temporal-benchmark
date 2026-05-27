from datetime import timedelta

from temporalio import workflow

# Tell the sandbox to treat 'activities' as a pass-through module so that
# the httpx import inside activities.py is not evaluated in the deterministic
# workflow sandbox context.
with workflow.unsafe.imports_passed_through():
    from activities import fetch_data


@workflow.defn
class FetchUrlWorkflow:
    @workflow.run
    async def run(self) -> str:
        return await workflow.execute_activity(
            fetch_data,
            "https://api.github.com/zen",
            start_to_close_timeout=timedelta(seconds=30),
        )
