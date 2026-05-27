import asyncio
import os
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

# Activity
@activity.defn
async def count_with_heartbeat(target: int) -> int:
    for i in range(1, target + 1):
        await asyncio.sleep(0.5)
        activity.heartbeat(i)
    return target

# Workflow
@workflow.defn
class HeartbeatWorkflow:
    @workflow.run
    async def run(self, target: int) -> int:
        return await workflow.execute_activity(
            count_with_heartbeat,
            target,
            start_to_close_timeout=timedelta(seconds=120),
            heartbeat_timeout=timedelta(seconds=5),
        )

async def main():
    api_key = os.environ.get("TEMPORAL_API_KEY")
    address = os.environ.get("TEMPORAL_ADDRESS")
    namespace = os.environ.get("TEMPORAL_NAMESPACE")
    run_id = os.environ.get("ZEALT_RUN_ID")

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    worker = Worker(
        client,
        task_queue="heartbeat-py",
        workflows=[HeartbeatWorkflow],
        activities=[count_with_heartbeat],
    )

    # Start worker in background
    worker_task = asyncio.create_task(worker.run())

    try:
        # Execute workflow
        result = await client.execute_workflow(
            HeartbeatWorkflow.run,
            5,
            id=f"heartbeat-wf-{run_id}",
            task_queue="heartbeat-py",
        )
        print(result)
    finally:
        # Stop worker
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
