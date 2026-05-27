import asyncio
import os
from datetime import timedelta

import temporalio.activity
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker


# ---------------------------------------------------------------------------
# Activity
# ---------------------------------------------------------------------------

@activity.defn(name="count_with_heartbeat")
async def count_with_heartbeat(target: int) -> int:
    for i in range(1, target + 1):
        await asyncio.sleep(0.5)
        activity.heartbeat(i)
    return target


# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------

@workflow.defn(name="HeartbeatWorkflow")
class HeartbeatWorkflow:
    @workflow.run
    async def run(self, target: int) -> int:
        result = await workflow.execute_activity(
            count_with_heartbeat,
            target,
            start_to_close_timeout=timedelta(seconds=120),
            heartbeat_timeout=timedelta(seconds=5),
        )
        return result


# ---------------------------------------------------------------------------
# Main entrypoint – worker + client in the same process
# ---------------------------------------------------------------------------

async def main() -> None:
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    run_id = os.environ["ZEALT_RUN_ID"]
    workflow_id = f"heartbeat-wf-{run_id}"
    task_queue = "heartbeat-py"

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[HeartbeatWorkflow],
        activities=[count_with_heartbeat],
    )

    # Start the worker as a background task so the client can run concurrently.
    worker_task = asyncio.create_task(worker.run())

    try:
        result = await client.execute_workflow(
            HeartbeatWorkflow.run,
            5,
            id=workflow_id,
            task_queue=task_queue,
        )
        print(result)
    finally:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
