FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio

RUN curl -sSf https://temporal.download/cli.sh | sh && \
    mv /root/.temporalio/bin/temporal /usr/local/bin/temporal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal project with starter, worker, and workflow files ready for interceptor implementation."

RUN mkdir -p /home/user/project && \
    cd /home/user/project && \
    cat >workflow.py <<'EOF'
from datetime import timedelta
from temporalio import activity, workflow

@activity.defn
async def say_hello(name: str) -> str:
    return f"Hello, {name}!"

@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            say_hello, name, start_to_close_timeout=timedelta(seconds=10)
        )
EOF
    
RUN cd /home/user/project && \
    cat >worker.py <<'EOF'
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import GreetingWorkflow, say_hello

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="greeting-tasks",
        workflows=[GreetingWorkflow],
        activities=[say_hello],
    )
    print("Starting worker...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
EOF

RUN cd /home/user/project && \
    cat >starter.py <<'EOF'
import asyncio
import uuid
from temporalio.client import Client
from workflow import GreetingWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        GreetingWorkflow.run,
        "Temporal",
        id=f"greeting-workflow-{uuid.uuid4()}",
        task_queue="greeting-tasks",
    )
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

RUN cd /home/user/project && \
    cat >interceptor.py <<'EOF'
import json
from temporalio import client, worker, activity

# TODO: Implement LoggingClientInterceptor and LoggingWorkerInterceptor here

EOF

# Container contents:
#   - temporal CLI installed
#   - temporalio Python SDK installed
#   - /home/user/project containing workflow.py, worker.py, starter.py, and interceptor.py

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
