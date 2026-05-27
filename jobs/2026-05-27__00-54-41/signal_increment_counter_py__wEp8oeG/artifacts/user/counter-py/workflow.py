from temporalio import workflow

@workflow.defn
class CounterWorkflow:
    def __init__(self) -> None:
        self._count = 0
        self._is_finished = False

    @workflow.run
    async def run(self) -> int:
        await workflow.wait_condition(lambda: self._is_finished)
        return self._count

    @workflow.signal
    def increment(self, n: int) -> None:
        self._count += n

    @workflow.signal
    def finish(self) -> None:
        self._is_finished = True

    @workflow.query
    def get_count(self) -> int:
        return self._count
