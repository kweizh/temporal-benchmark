import random

from temporalio import activity


@activity.defn(name="pick_discount")
async def pick_discount() -> int:
    """Pick a random discount from the allowed set. Non-determinism is safe in Activities."""
    return random.choice([0, 5, 10, 15, 20])
