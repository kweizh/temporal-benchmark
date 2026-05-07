from datetime import timedelta
from temporalio import activity, workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError

@activity.defn
async def failing_activity() -> str:
    raise ValueError("failing")

@workflow.defn
class RetryWorkflow:
    @workflow.run
    async def run(self) -> str:
        try:
            return await workflow.execute_activity(
                failing_activity,
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=RetryPolicy(
                    maximum_attempts=5,
                    initial_interval=timedelta(seconds=2),
                    backoff_coefficient=1.0,
                ),
            )
        except ActivityError:
            return "Failed as expected"
