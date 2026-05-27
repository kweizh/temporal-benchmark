import random
from temporalio import activity

ALLOWED_DISCOUNTS = [0, 5, 10, 15, 20]


@activity.defn(name="pick_discount")
async def pick_discount() -> int:
    return random.choice(ALLOWED_DISCOUNTS)
