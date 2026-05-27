"""CounterWorkflow: accumulates values via Signals, exposes state via Query."""

from temporalio import workflow


@workflow.defn(name="CounterWorkflow")
class CounterWorkflow:
    def __init__(self) -> None:
        self._counter: int = 0
        self._finished: bool = False

    @workflow.run
    async def run(self) -> int:
        # Block until the finish signal sets _finished to True
        await workflow.wait_condition(lambda: self._finished)
        return self._counter

    @workflow.signal
    async def increment(self, n: int) -> None:
        self._counter += n

    @workflow.signal
    async def finish(self) -> None:
        self._finished = True

    @workflow.query
    def get_count(self) -> int:
        return self._counter
