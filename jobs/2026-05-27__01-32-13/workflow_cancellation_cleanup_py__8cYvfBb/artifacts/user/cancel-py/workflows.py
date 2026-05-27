from __future__ import annotations

import asyncio
from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import release_resources


@workflow.defn
class LongJobWorkflow:
    @workflow.run
    async def run(self, job_id: str) -> None:
        try:
            await workflow.sleep(timedelta(minutes=10))
        except asyncio.CancelledError:
            await asyncio.shield(
                workflow.execute_activity(
                    release_resources,
                    job_id,
                    start_to_close_timeout=timedelta(seconds=30),
                )
            )
            raise
