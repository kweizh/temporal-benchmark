import asyncio
from datetime import timedelta
from temporalio import workflow

@workflow.defn
class StatefulWorkflow:
    def __init__(self) -> None:
        self._counter = 0
        self._finish = False

    @workflow.run
    async def run(self) -> int:
        # Loop for at most 10 iterations
        for _ in range(10):
            if self._finish:
                break
            
            # Wait for 1 second or until the finish signal is received
            # Using wait_condition with timeout to ensure we can respond to signals or proceed
            await workflow.wait_condition(lambda: self._finish, timeout=timedelta(seconds=1))
            
            if self._finish:
                break
                
            self._counter += 1
            
        return self._counter

    @workflow.query
    def get_counter(self) -> int:
        return self._counter

    @workflow.signal
    def finish(self) -> None:
        self._finish = True
