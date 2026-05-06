FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal python project with a non-deterministic workflow."

RUN mkdir -p /home/user/temporal-project && \
    cd /home/user/temporal-project && \
    cat >workflow.py <<'EOF'
from datetime import datetime
from temporalio import workflow

@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"Hello, {name}! The time is {current_time}."
EOF

RUN cd /home/user/temporal-project && \
    cat >test_workflow.py <<'EOF'
import os
import asyncio
import uuid
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import GreetingWorkflow

async def main():
    client = await Client.connect(
        os.getenv("TEMPORAL_ADDRESS"),
        namespace=os.getenv("TEMPORAL_NAMESPACE"),
        api_key=os.getenv("TEMPORAL_API_KEY")
    )

    task_queue = f"test-queue-{uuid.uuid4()}"
    
    async with Worker(
        client,
        task_queue=task_queue,
        workflows=[GreetingWorkflow],
    ):
        result = await client.execute_workflow(
            GreetingWorkflow.run,
            "World",
            id=f"wf-id-{uuid.uuid4()}",
            task_queue=task_queue
        )
        print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Container contents:
#   - temporalio installed
#   - /home/user/temporal-project with workflow.py using datetime.now()
#   - test_workflow.py to run the workflow

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
