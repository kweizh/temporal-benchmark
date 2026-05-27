import asyncio
from temporalio import workflow


@workflow.defn
class StatefulWorkflow:
    """Workflow that maintains an incrementing counter, exposes it via a Query,
    and accepts a Signal to stop early."""

    def __init__(self) -> None:
        self._counter: int = 0
        self._should_finish: bool = False

    @workflow.run
    async def run(self) -> int:
        max_iterations = 10

        for _ in range(max_iterations):
            # Check stop flag before sleeping
            if self._should_finish:
                break

            # Sleep ~1 second, but wake early if the finish signal arrives
            try:
                await workflow.wait_condition(
                    lambda: self._should_finish, timeout=1.0
                )
            except asyncio.TimeoutError:
                pass

            # Increment after the sleep/wait
            self._counter += 1

            # Check stop flag after incrementing
            if self._should_finish:
                break

        return self._counter

    @workflow.query
    def get_counter(self) -> int:
        """Return the current value of the counter without mutating state."""
        return self._counter

    @workflow.signal
    def finish(self) -> None:
        """Signal the workflow to stop incrementing and return the current counter."""
        self._should_finish = True
