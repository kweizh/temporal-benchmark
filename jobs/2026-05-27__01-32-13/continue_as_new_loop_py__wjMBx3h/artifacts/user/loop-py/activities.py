from temporalio import activity


@activity.defn
async def increment_counter(value: int) -> int:
    with open("/workspace/loop.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"{value}\n")
    return value
