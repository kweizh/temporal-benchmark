import os
from datetime import timedelta
from temporalio import activity, workflow

@activity.defn
async def increment_counter(value: int) -> int:
    workspace_path = "/workspace"
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)
    
    log_file = os.path.join(workspace_path, "loop.log")
    with open(log_file, "a") as f:
        f.write(f"{value}\n")
    
    return value

@workflow.defn
class LongLoopWorkflow:
    @workflow.run
    async def run(self, start: int, target: int) -> int:
        current_value = start
        iterations_in_this_run = 0
        
        while current_value < target:
            current_value = await workflow.execute_activity(
                increment_counter,
                current_value + 1,
                start_to_close_timeout=timedelta(seconds=5),
            )
            iterations_in_this_run += 1
            
            if iterations_in_this_run >= 10 and current_value < target:
                workflow.continue_as_new(args=[current_value, target])
        
        return current_value
