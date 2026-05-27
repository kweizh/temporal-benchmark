from __future__ import annotations

from temporalio import activity
from temporalio.exceptions import ApplicationError


@activity.defn
async def flaky_task() -> None:
    info = activity.info()
    attempt = info.attempt
    with open("/workspace/attempts.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"attempt {attempt}\n")
    raise ApplicationError("boom")
