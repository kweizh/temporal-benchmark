import os
from temporalio import activity


@activity.defn(name="notify")
async def notify(message: str) -> str:
    log_path = "/workspace/reminder.log"
    os.makedirs("/workspace", exist_ok=True)
    line = f"Notified: {message}"
    with open(log_path, "a") as f:
        f.write(line + "\n")
    return line
