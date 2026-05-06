FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio==1.6.0

RUN curl -sSf https://temporal.download/cli.sh | sh && \
    cp /root/.temporalio/bin/temporal /usr/local/bin/temporal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal python project with workflow, worker, and starter files."

RUN mkdir -p /home/user/temporal-project && \
    cd /home/user/temporal-project && \
    cat >workflow.py <<'EOF'
from temporalio import workflow

@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return f"Hello, {name}!"
EOF

RUN cd /home/user/temporal-project && \
    cat >worker.py <<'EOF'
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import GreetingWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[GreetingWorkflow],
    )
    print("Starting worker...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
EOF

RUN cd /home/user/temporal-project && \
    cat >starter.py <<'EOF'
import asyncio
from temporalio.client import Client
from workflow import GreetingWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        GreetingWorkflow.run,
        "Temporal",
        id="my-workflow",
        task_queue="my-task-queue",
    )
    print(f"Workflow result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Container contents:
#   - temporalio python SDK installed
#   - temporal CLI installed
#   - /home/user/temporal-project with workflow.py, worker.py, starter.py

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]