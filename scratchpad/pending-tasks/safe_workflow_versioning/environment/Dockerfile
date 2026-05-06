FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio pytest-asyncio

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal project with a workflow lacking safe versioning, and an existing history file."

RUN mkdir -p /home/user/project
WORKDIR /home/user/project

# Generate the history.json
RUN cat > generate_history.py <<'EOF'
import asyncio
from datetime import timedelta
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from temporalio import workflow, activity

@activity.defn
async def send_greeting(name: str) -> str:
    return f"Hello, {name}!"

@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            send_greeting,
            name,
            start_to_close_timeout=timedelta(seconds=5),
        )

async def main():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="my-task-queue",
            workflows=[GreetingWorkflow],
            activities=[send_greeting],
        ):
            handle = await env.client.start_workflow(
                GreetingWorkflow.run,
                "Temporal",
                id="my-workflow-id",
                task_queue="my-task-queue",
            )
            await handle.result()
            history = await handle.fetch_history()
            with open("history.json", "w") as f:
                f.write(history.to_json())

if __name__ == "__main__":
    asyncio.run(main())
EOF

RUN python3 generate_history.py && rm generate_history.py

# Create the unpatched workflow
RUN cat > workflow.py <<'EOF'
from datetime import timedelta
from temporalio import workflow, activity

@activity.defn
async def send_greeting(name: str) -> str:
    return f"Hello, {name}!"

@activity.defn
async def send_followup(name: str) -> str:
    return f"Followup for {name}!"

@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        greeting = await workflow.execute_activity(
            send_greeting,
            name,
            start_to_close_timeout=timedelta(seconds=5),
        )
        
        # TODO: Safely add the send_followup activity using workflow.patched
        
        return greeting
EOF

# Create the test file
RUN cat > test_workflow.py <<'EOF'
import asyncio
import pytest
from temporalio.worker import Replayer
from temporalio.client import WorkflowHistory
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from workflow import GreetingWorkflow, send_greeting, send_followup

@pytest.mark.asyncio
async def test_replay_old_history():
    with open("history.json", "r") as f:
        hist_str = f.read()
    replayer = Replayer(workflows=[GreetingWorkflow])
    # This will raise an exception if NondeterminismError occurs
    await replayer.replay_workflow(WorkflowHistory.from_json("my-workflow-id", hist_str))

@pytest.mark.asyncio
async def test_new_execution():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="my-task-queue",
            workflows=[GreetingWorkflow],
            activities=[send_greeting, send_followup],
        ):
            handle = await env.client.start_workflow(
                GreetingWorkflow.run,
                "Temporal",
                id="new-workflow-id",
                task_queue="my-task-queue",
            )
            result = await handle.result()
            history = await handle.fetch_history()
            
            events = list(history.events)
            activity_count = sum(1 for e in events if e.HasField("activity_task_scheduled_event_attributes"))
            assert activity_count == 2, "Expected 2 activities to be scheduled in the new execution"
EOF

# Container contents:
#   - temporalio and pytest-asyncio installed
#   - /home/user/project/history.json generated
#   - /home/user/project/workflow.py (unpatched workflow)
#   - /home/user/project/test_workflow.py (tests for replay and new execution)

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
