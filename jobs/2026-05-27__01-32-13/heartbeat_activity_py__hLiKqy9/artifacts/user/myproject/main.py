import asyncio
import os
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

TASK_QUEUE = "heartbeat-py"


@activity.defn(name="count_with_heartbeat")
async def count_with_heartbeat(target: int) -> int:
    for i in range(1, target + 1):
        await asyncio.sleep(0.5)
        activity.heartbeat(i)
    return target


@workflow.defn(name="HeartbeatWorkflow")
class HeartbeatWorkflow:
    @workflow.run
    async def run(self, target: int) -> int:
        return await workflow.execute_activity(
            count_with_heartbeat,
            target,
            start_to_close_timeout=timedelta(seconds=120),
            heartbeat_timeout=timedelta(seconds=5),
        )


async def run() -> None:
    temporal_address = os.environ["TEMPORAL_ADDRESS"]
    temporal_namespace = os.environ["TEMPORAL_NAMESPACE"]
    temporal_api_key = os.environ["TEMPORAL_API_KEY"]
    run_id = os.environ["ZEALT_RUN_ID"]

    workflow_id = f"heartbeat-wf-{run_id}"

    client = await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=True,
    )

    async with Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[HeartbeatWorkflow],
        activities=[count_with_heartbeat],
    ):
        result = await client.execute_workflow(
            HeartbeatWorkflow.run,
            5,
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(run())
