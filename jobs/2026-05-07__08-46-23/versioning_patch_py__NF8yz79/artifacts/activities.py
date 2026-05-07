from temporalio import activity

@activity.defn
async def old_activity() -> str:
    return "old_result"

@activity.defn
async def new_activity() -> str:
    return "new_result"
