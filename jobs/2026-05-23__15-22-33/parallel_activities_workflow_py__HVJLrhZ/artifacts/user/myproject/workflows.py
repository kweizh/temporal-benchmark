import asyncio
from datetime import timedelta
from temporalio import workflow

# Import activity, but we only need the type hint for execute_activity
with workflow.unsafe.imports_passed_through():
    from activities import fetch_url

@workflow.defn
class ParallelFetchWorkflow:
    @workflow.run
    async def run(self, urls: list[str]) -> dict[str, int]:
        # Schedule activities concurrently
        tasks = [
            workflow.execute_activity(
                fetch_url,
                url,
                start_to_close_timeout=timedelta(seconds=30)
            )
            for url in urls
        ]
        
        # Await all tasks together using asyncio.gather
        results = await asyncio.gather(*tasks)
        
        # Map URLs to results
        return dict(zip(urls, results))
