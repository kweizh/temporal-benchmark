import asyncio
from datetime import timedelta
from temporalio import workflow

@workflow.defn
class SubscriptionWorkflow:
    def __init__(self) -> None:
        self._tier = "basic"
        self._is_canceled = False

    @workflow.run
    async def run(self) -> str:
        workflow.logger.info("Subscription workflow started")
        
        # We'll run for up to 3 cycles if not canceled, 
        # just to show it works in a loop.
        for cycle in range(1, 4):
            if self._is_canceled:
                break
                
            workflow.logger.info(f"Starting billing cycle {cycle} with tier: {self._tier}")
            
            # Wait for 30 seconds or until canceled
            try:
                await workflow.wait_condition(
                    lambda: self._is_canceled,
                    timeout=timedelta(seconds=30)
                )
                canceled = True
            except asyncio.TimeoutError:
                canceled = False
            
            if canceled:
                workflow.logger.info("Cancellation received during cycle")
                break
            else:
                workflow.logger.info(f"Billing cycle {cycle} completed successfully")
                
        status = "canceled" if self._is_canceled else "completed"
        result = f"Subscription {status}. Final tier: {self._tier}"
        workflow.logger.info(result)
        return result

    @workflow.signal
    def upgrade(self, new_tier: str) -> None:
        self._tier = new_tier
        workflow.logger.info(f"Signal received: Upgrade to {new_tier}")

    @workflow.signal
    def cancel(self) -> None:
        self._is_canceled = True
        workflow.logger.info("Signal received: Cancel subscription")
