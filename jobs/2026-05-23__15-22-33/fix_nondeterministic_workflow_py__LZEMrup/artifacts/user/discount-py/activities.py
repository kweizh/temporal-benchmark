import random
from temporalio import activity

@activity.defn(name="pick_discount")
async def pick_discount() -> int:
    return random.choice([0, 5, 10, 15, 20])
