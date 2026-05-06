FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio pytest-asyncio

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal Python project with a workflow missing a query method."

RUN mkdir -p /home/user/project && \
    cd /home/user/project && \
    cat >workflow.py <<'EOF'
from temporalio import workflow

@workflow.defn
class UserProfileWorkflow:
    def __init__(self) -> None:
        self._email = ""

    @workflow.run
    async def run(self) -> None:
        # Keep workflow running to receive signals
        await workflow.wait_condition(lambda: False)

    @workflow.signal
    def update_email(self, email: str) -> None:
        self._email = email
EOF

RUN cd /home/user/project && \
    cat >test_workflow.py <<'EOF'
import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from workflow import UserProfileWorkflow
import uuid

@pytest.mark.asyncio
async def test_query_email():
    async with WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[UserProfileWorkflow],
        ):
            workflow_id = f"user-profile-{uuid.uuid4()}"
            handle = await env.client.start_workflow(
                UserProfileWorkflow.run,
                id=workflow_id,
                task_queue="test-queue",
            )
            
            await handle.signal(UserProfileWorkflow.update_email, "test@example.com")
            
            # Query the workflow
            email = await handle.query("get_email")
            assert email == "test@example.com"
EOF

# Container contents:
#   - temporalio and pytest-asyncio installed
#   - /home/user/project contains workflow.py and test_workflow.py

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
