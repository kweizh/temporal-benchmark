FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSf https://temporal.download/cli.sh | sh && \
    mv /root/.temporalio/bin/temporal /usr/local/bin/temporal

RUN pip3 install --break-system-packages temporalio

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal project with initial workflow code."

RUN mkdir -p /home/user/temporal-project && \
    cd /home/user/temporal-project && \
    cat >workflow.py <<'EOF'
from datetime import timedelta
from temporalio import workflow

@workflow.defn
class ProcessingWorkflow:
    @workflow.run
    async def run(self) -> str:
        # Processing logic goes here
        await workflow.sleep(timedelta(seconds=1))
        return "Done"
EOF

RUN cd /home/user/temporal-project && \
    cat >worker.py <<'EOF'
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import ProcessingWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="processing-task-queue",
        workflows=[ProcessingWorkflow],
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
EOF

RUN cd /home/user/temporal-project && \
    cat >starter.py <<'EOF'
import asyncio
import uuid
from temporalio.client import Client
from workflow import ProcessingWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        ProcessingWorkflow.run,
        id=f"processing-workflow-{uuid.uuid4()}",
        task_queue="processing-task-queue",
    )
    print(f"Workflow result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Container contents:
#   - temporalio installed for python
#   - temporal CLI installed
#   - /home/user/temporal-project with initial workflow.py, worker.py, starter.py

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
