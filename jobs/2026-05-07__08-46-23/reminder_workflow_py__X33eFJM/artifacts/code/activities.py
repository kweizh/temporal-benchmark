from temporalio import activity

@activity.defn
async def notify(message: str) -> str:
    return "Notified: " + message
