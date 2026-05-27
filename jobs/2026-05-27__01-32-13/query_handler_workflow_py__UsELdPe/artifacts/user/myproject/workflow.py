from __future__ import annotations

from temporalio import workflow


@workflow.defn
class StatefulWorkflow:
    def __init__(self) -> None:
        self.counter = 0
        self._stop = False

    @workflow.run
    async def run(self) -> int:
        max_iterations = 10
        for _ in range(max_iterations):
            self.counter += 1
            await workflow.sleep(1)
            if self._stop:
                break
        return self.counter

    @workflow.query
    def get_counter(self) -> int:
        return self.counter

    @workflow.signal
    def finish(self) -> None:
        self._stop = True
