import asyncio
import os
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

# Activity Definition
@activity.defn
async def release_resources(job_id: str) -> None:
    log_path = "/workspace/cleanup.log"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"released:{job_id}\n")
    activity.logger.info(f"Resources released for job: {job_id}")

# Workflow Definition
@workflow.defn
class LongJobWorkflow:
    @workflow.run
    async def run(self, job_id: str) -> None:
        try:
            workflow.logger.info(f"Starting long job for: {job_id}")
            await workflow.sleep(timedelta(minutes=10))
            workflow.logger.info("Long job completed (unexpectedly)")
        except asyncio.CancelledError:
            workflow.logger.info(f"Cancellation received for job: {job_id}. Starting cleanup.")
            # Shield the cleanup activity so it survives cancellation
            await asyncio.shield(
                workflow.execute_activity(
                    release_resources,
                    job_id,
                    start_to_close_timeout=timedelta(seconds=30),
                )
            )
            workflow.logger.info(f"Cleanup completed for job: {job_id}. Re-raising CancelledError.")
            raise
