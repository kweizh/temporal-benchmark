import asyncio
from datetime import timedelta
from temporalio import workflow

@workflow.defn
class CounterWorkflow:
    def __init__(self) -> None:
        self._counter: int = 0
        self._finished: bool = False

    @workflow.run
    async def run(self) -> int:
        await workflow.wait_condition(lambda: self._finished)
        return self._counter

    @workflow.signal
    def increment(self, n: int) -> None:
        self._counter += n

    @workflow.signal
    def finish(self) -> None:
        self._finished = True

    @workflow.query
    def get_count(self) -> int:
        return self._counter
