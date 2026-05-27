import temporalio.activity
from temporalio.exceptions import ApplicationError


@temporalio.activity.defn
async def flaky_task() -> None:
    """Activity that always fails, logging each attempt."""
    attempt = temporalio.activity.info().attempt
    with open("/workspace/attempts.log", "a") as f:
        f.write(f"Attempt {attempt}\n")
    raise ApplicationError("boom")
