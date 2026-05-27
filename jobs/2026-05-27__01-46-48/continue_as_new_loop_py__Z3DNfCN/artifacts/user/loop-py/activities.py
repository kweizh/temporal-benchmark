from temporalio import activity


@activity.defn
async def increment_counter(value: int) -> int:
    """Appends the given value to /workspace/loop.log and returns it."""
    with open("/workspace/loop.log", "a") as f:
        f.write(f"{value}\n")
    return value
