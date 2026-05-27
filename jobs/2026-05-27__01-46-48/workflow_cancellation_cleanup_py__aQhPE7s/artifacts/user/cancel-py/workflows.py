"""Temporal workflows for the cancel-py project."""

import asyncio
from datetime import timedelta

from temporalio import workflow

# Import activity with sandbox-safe import
with workflow.unsafe.imports_passed_through():
    from activities import release_resources


@workflow.defn
class LongJobWorkflow:
    """A long-running workflow that cleans up shielded on cancellation."""

    @workflow.run
    async def run(self, job_id: str) -> None:
        try:
            # Main work: sleep for 10 minutes
            await workflow.sleep(timedelta(minutes=10))
        except asyncio.CancelledError:
            # Cancellation received – run cleanup shielded so it is not
            # itself cancelled while the workflow task is being cancelled.
            await asyncio.shield(
                workflow.execute_activity(
                    release_resources,
                    job_id,
                    start_to_close_timeout=timedelta(seconds=30),
                )
            )
            # Re-raise so the workflow ends in CANCELED state.
            raise
