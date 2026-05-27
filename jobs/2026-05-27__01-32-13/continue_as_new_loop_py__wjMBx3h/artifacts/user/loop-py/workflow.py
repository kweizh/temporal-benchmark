from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import increment_counter


@workflow.defn
class LongLoopWorkflow:
    @workflow.run
    async def run(self, start: int, target: int) -> int:
        current = start
        for _ in range(10):
            if current >= target:
                return current
            current = await workflow.execute_activity(
                increment_counter,
                current + 1,
                start_to_close_timeout=timedelta(seconds=10),
            )
            if current == target:
                return current
        workflow.continue_as_new(current, target)
        return current
