from datetime import timedelta

import temporalio.workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError

with temporalio.workflow.unsafe.imports_passed_through():
    from activities import flaky_task


@temporalio.workflow.defn
class FlakyWorkflow:
    @temporalio.workflow.run
    async def run(self) -> str:
        retry_policy = RetryPolicy(
            maximum_attempts=5,
            initial_interval=timedelta(seconds=2),
            backoff_coefficient=1.0,
        )
        try:
            await temporalio.workflow.execute_activity(
                flaky_task,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy,
            )
        except ActivityError:
            return "failed after 5 attempts"
        return "succeeded"
