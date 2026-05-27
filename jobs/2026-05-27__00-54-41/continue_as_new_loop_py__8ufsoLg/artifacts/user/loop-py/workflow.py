import os
from datetime import timedelta
from temporalio import activity, workflow

@activity.defn
async def increment_counter(val: int) -> int:
    with open("/workspace/loop.log", "a") as f:
        f.write(f"{val}\n")
    return val

@workflow.defn
class LongLoopWorkflow:
    @workflow.run
    async def run(self, start: int, target: int) -> int:
        current = start
        for i in range(10):
            if current >= target:
                return current
            
            current += 1
            await workflow.execute_activity(
                increment_counter,
                current,
                start_to_close_timeout=timedelta(seconds=5),
            )
            
            if current >= target:
                return current
                
        workflow.continue_as_new(args=[current, target])
