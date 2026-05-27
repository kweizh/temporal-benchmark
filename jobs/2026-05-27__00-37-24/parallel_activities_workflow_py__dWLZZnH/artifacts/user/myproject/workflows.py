import asyncio
from datetime import timedelta
from temporalio import workflow

# Import activity, but only for type hinting
with workflow.unsafe.imports_passed_through():
    from activities import fetch_url

@workflow.defn
class ParallelFetchWorkflow:
    @workflow.run
    async def run(self, urls: list[str]) -> dict[str, int]:
        tasks = [
            workflow.execute_activity(
                fetch_url,
                url,
                start_to_close_timeout=timedelta(seconds=30)
            )
            for url in urls
        ]
        
        results = await asyncio.gather(*tasks)
        
        return dict(zip(urls, results))
