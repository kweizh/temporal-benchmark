"""Temporal activities for the cancel-py project."""

from temporalio import activity


@activity.defn
async def release_resources(job_id: str) -> None:
    """Append 'released:<job_id>' to /workspace/cleanup.log."""
    log_path = "/workspace/cleanup.log"
    line = f"released:{job_id}\n"
    with open(log_path, "a") as f:
        f.write(line)
    activity.logger.info("Released resources for job_id=%s", job_id)
