from temporalio import workflow


@workflow.defn
class CounterWorkflow:
    def __init__(self) -> None:
        self._count = 0
        self._finished = False

    @workflow.run
    async def run(self) -> int:
        await workflow.wait_condition(lambda: self._finished)
        return self._count

    @workflow.signal
    async def increment(self, n: int) -> None:
        self._count += n

    @workflow.signal
    async def finish(self) -> None:
        self._finished = True

    @workflow.query
    def get_count(self) -> int:
        return self._count
