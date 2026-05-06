FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio

RUN curl -sSf https://temporal.download/cli.sh | sh && \
    cp /root/.temporalio/bin/temporal /usr/local/bin/temporal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal Python project with an old workflow history recorded."

RUN mkdir -p /home/user/temporal_project

# Create the initial project files
RUN cat <<'EOF' > /home/user/temporal_project/workflow.py
from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import old_activity, new_activity

@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self) -> str:
        return await workflow.execute_activity(
            old_activity,
            start_to_close_timeout=timedelta(seconds=5),
        )
EOF

RUN cat <<'EOF' > /home/user/temporal_project/activities.py
from temporalio import activity

@activity.defn
async def old_activity() -> str:
    return "old_result"

@activity.defn
async def new_activity() -> str:
    return "new_result"
EOF

RUN cat <<'EOF' > /home/user/temporal_project/worker.py
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import MyWorkflow
from activities import old_activity, new_activity

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[MyWorkflow],
        activities=[old_activity, new_activity],
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
EOF

RUN cat <<'EOF' > /home/user/temporal_project/run_old_workflow.py
import asyncio
from temporalio.client import Client

async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        "MyWorkflow",
        id="old-workflow-id",
        task_queue="my-task-queue",
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Start temporal server, run the worker, execute the workflow, export history, and kill everything
RUN (temporal server start-dev --headless &) && \
    sleep 5 && \
    cd /home/user/temporal_project && \
    python3 worker.py & \
    WORKER_PID=$! && \
    sleep 2 && \
    cd /home/user/temporal_project && \
    python3 run_old_workflow.py && \
    temporal workflow show --workflow-id old-workflow-id --output json > history.json && \
    kill $WORKER_PID && \
    pkill temporal

# Create the verification scripts
RUN cat <<'EOF' > /home/user/temporal_project/verify_replay.py
import asyncio
import json
from temporalio.worker import Replayer
from temporalio.client import WorkflowHistory
from workflow import MyWorkflow

async def main():
    with open("history.json", "r") as f:
        history_dict = json.load(f)
    
    # Extract the history events from the JSON output of `temporal workflow show`
    # The JSON structure might be nested depending on the CLI version.
    # Usually `events` is at the top level.
    if "events" in history_dict:
        events = history_dict["events"]
    else:
        # Fallback if structure is different
        events = history_dict
        
    history = WorkflowHistory.from_json(json.dumps({"events": events}))
    
    replayer = Replayer(workflows=[MyWorkflow])
    await replayer.replay_workflow(history)
    print("Replay successful!")

if __name__ == "__main__":
    asyncio.run(main())
EOF

RUN cat <<'EOF' > /home/user/temporal_project/test_new_workflow.py
import asyncio
from temporalio.client import Client
from workflow import MyWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        "MyWorkflow",
        id="new-workflow-id",
        task_queue="my-task-queue",
    )
    if result != "new_result":
        raise Exception(f"Expected 'new_result', got {result}")
    print("New workflow successful!")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Container contents:
#   - temporal CLI installed
#   - temporalio python package installed
#   - /home/user/temporal_project with workflow, activities, worker, and history.json

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
