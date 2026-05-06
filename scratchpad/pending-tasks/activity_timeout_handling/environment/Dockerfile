FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSf https://temporal.download/cli.sh | sh
ENV PATH="/root/.temporalio/bin:${PATH}"

RUN pip3 install --break-system-packages temporalio

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal environment for activity timeout handling task"

RUN mkdir -p /home/user/temporal_project && \
    cd /home/user/temporal_project && \
    cat >workflow.py <<'EOF'
import asyncio
from datetime import timedelta
from temporalio import activity, workflow

@activity.defn
async def process_data(data: str) -> str:
    # Simulate a slow process
    await asyncio.sleep(5)
    return f"Processed {data}"

@workflow.defn
class DataProcessingWorkflow:
    @workflow.run
    async def run(self, data: str) -> str:
        # Developer mistakenly set start_to_close_timeout to 2 seconds
        # They also forgot schedule_to_close_timeout
        result = await workflow.execute_activity(
            process_data,
            data,
            start_to_close_timeout=timedelta(seconds=2)
        )
        return result
EOF

RUN cd /home/user/temporal_project && \
    cat >run_workflow.py <<'EOF'
import asyncio
import sys
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import DataProcessingWorkflow, process_data

async def main():
    client = await Client.connect("localhost:7233")
    
    # Run a worker
    worker = Worker(
        client,
        task_queue="data-processing-queue",
        workflows=[DataProcessingWorkflow],
        activities=[process_data],
    )
    
    # Run the worker and the workflow concurrently
    async def run_worker():
        await worker.run()
        
    worker_task = asyncio.create_task(run_worker())
    
    try:
        result = await client.execute_workflow(
            DataProcessingWorkflow.run,
            "sample_data",
            id="data-processing-workflow-id",
            task_queue="data-processing-queue",
        )
        print(result)
    except Exception as e:
        print(f"Workflow failed: {e}")
        sys.exit(1)
    finally:
        worker_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Container contents:
#   - temporal cli installed
#   - temporalio python sdk installed
#   - /home/user/temporal_project with workflow.py and run_workflow.py

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
