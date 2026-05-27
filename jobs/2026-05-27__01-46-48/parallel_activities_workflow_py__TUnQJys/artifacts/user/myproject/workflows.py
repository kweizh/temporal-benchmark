"""Temporal workflows — must be deterministic; no I/O imports here."""

import asyncio
from datetime import timedelta

from temporalio import workflow

# Import the activity function inside the sandbox-safe with block so that
# the sandbox does not try to import httpx in workflow context.
with workflow.unsafe.imports_passed_through():
    from activities import fetch_url


@workflow.defn
class ParallelFetchWorkflow:
    @workflow.run
    async def run(self, urls: list[str]) -> dict[str, int]:
        # Build awaitables for all URLs without awaiting individually —
        # this fans out all activity schedules concurrently.
        tasks = [
            workflow.execute_activity(
                fetch_url,
                url,
                start_to_close_timeout=timedelta(seconds=30),
            )
            for url in urls
        ]
        # Await all in parallel.
        results: list[int] = await asyncio.gather(*tasks)
        return dict(zip(urls, results))
