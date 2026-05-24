from temporalio import activity
from temporalio.exceptions import ApplicationError

@activity.defn
async def flaky_task() -> None:
    attempt = activity.info().attempt
    with open("/workspace/attempts.log", "a") as f:
        f.write(f"Attempt {attempt}\n")
    raise ApplicationError("boom")
