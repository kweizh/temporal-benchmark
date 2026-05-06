FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio==1.18.2 pytest-asyncio==0.23.5

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal Python SDK environment with a failing activity and incomplete workflow."

RUN mkdir -p /home/user/project && \
    cd /home/user/project && \
    cat >activity.py <<'EOF'
from temporalio import activity

attempts = 0

@activity.defn
async def always_fail() -> None:
    global attempts
    attempts += 1
    raise RuntimeError("I failed")
EOF

RUN cd /home/user/project && \
    cat >workflow.py <<'EOF'
from datetime import timedelta
from temporalio import workflow
from temporalio.exceptions import ActivityError

with workflow.unsafe.imports_passed_through():
    from activity import always_fail

@workflow.defn
class RetryWorkflow:
    @workflow.run
    async def run(self) -> str:
        try:
            # TODO: Execute `always_fail` activity with a RetryPolicy
            # The policy must have:
            # - initial_interval of 1 second
            # - backoff_coefficient of 2.0
            # - maximum_attempts of 3
            # Use start_to_close_timeout=timedelta(seconds=5)
            
            await workflow.execute_activity(
                always_fail,
                start_to_close_timeout=timedelta(seconds=5),
            )
            return "Success"
        except ActivityError:
            return "Failed after 3 attempts"
EOF

RUN cd /home/user/project && \
    cat >test_workflow.py <<'EOF'
import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from workflow import RetryWorkflow
import activity

@pytest.mark.asyncio
async def test_retry_workflow():
    activity.attempts = 0
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[RetryWorkflow],
            activities=[activity.always_fail],
        ):
            result = await env.client.execute_workflow(
                RetryWorkflow.run,
                id="test-retry-id",
                task_queue="test-queue",
            )
            assert result == "Failed after 3 attempts", f"Expected 'Failed after 3 attempts', got {result}"
            assert activity.attempts == 3, f"Expected 3 attempts, got {activity.attempts}"
EOF

# Container contents:
#   - temporalio and pytest-asyncio installed
#   - /home/user/project  — Temporal project
#   - activity.py with always_fail activity
#   - workflow.py with incomplete RetryWorkflow
#   - test_workflow.py for local verification
CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
