from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import increment_counter

BATCH_SIZE = 10


@workflow.defn
class LongLoopWorkflow:
    """
    Increments a counter from `start+1` up to `target`, logging each value
    via the `increment_counter` activity.  Every BATCH_SIZE (10) activity
    completions the workflow calls `continue_as_new` to keep the event
    history bounded.
    """

    @workflow.run
    async def run(self, start: int, target: int) -> int:
        current = start
        for _ in range(BATCH_SIZE):
            if current >= target:
                break
            next_value = current + 1
            recorded = await workflow.execute_activity(
                increment_counter,
                next_value,
                start_to_close_timeout=timedelta(seconds=30),
            )
            current = recorded

        if current < target:
            # Hand off to a new run with the updated start value.
            workflow.continue_as_new(args=[current, target])

        return target
