from temporalio import activity
import os

@activity.def
async def notify(message: str) -> str:
    log_file = "/workspace/reminder.log"
    # Ensure directory exists (though /workspace is requested to exist)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    with open(log_file, "a") as f:
        f.write(f"Notified: {message}\n")
    
    return f"Notified: {message}"
