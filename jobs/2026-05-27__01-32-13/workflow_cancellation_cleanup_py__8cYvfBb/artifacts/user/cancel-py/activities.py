from __future__ import annotations

from temporalio import activity


@activity.defn
def release_resources(job_id: str) -> None:
    with open("/workspace/cleanup.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"released:{job_id}\n")
