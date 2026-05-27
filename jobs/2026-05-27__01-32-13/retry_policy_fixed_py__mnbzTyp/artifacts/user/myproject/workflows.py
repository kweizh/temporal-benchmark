from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError


@workflow.defn
class FlakyWorkflow:
    @workflow.run
    async def run(self) -> str:
        try:
            await workflow.execute_activity(
                "flaky_task",
                retry_policy=RetryPolicy(
                    maximum_attempts=5,
                    initial_interval=timedelta(seconds=2),
                    backoff_coefficient=1.0,
                ),
                start_to_close_timeout=timedelta(seconds=5),
            )
        except ActivityError:
            return "failed after 5 attempts"
        return "unexpected success"
