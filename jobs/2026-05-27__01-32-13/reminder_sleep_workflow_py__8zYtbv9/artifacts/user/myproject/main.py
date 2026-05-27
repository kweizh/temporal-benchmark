import asyncio
import os
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker


@activity.defn
async def notify(message: str) -> str:
    os.makedirs("/workspace", exist_ok=True)
    log_path = "/workspace/reminder.log"
    line = f"Notified: {message}\n"
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(line)
    return f"Notified: {message}"


@workflow.defn
class ReminderWorkflow:
    @workflow.run
    async def run(self, message: str, delay_seconds: int) -> str:
        await asyncio.sleep(delay_seconds)
        return await workflow.execute_activity(
            notify,
            message,
            start_to_close_timeout=timedelta(seconds=30),
        )


async def async_main() -> None:
    temporal_address = os.environ["TEMPORAL_ADDRESS"]
    temporal_namespace = os.environ["TEMPORAL_NAMESPACE"]
    temporal_api_key = os.environ["TEMPORAL_API_KEY"]
    zealt_run_id = os.environ["ZEALT_RUN_ID"]

    client = await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=True,
    )

    worker = Worker(
        client,
        task_queue="reminder-py",
        workflows=[ReminderWorkflow],
        activities=[notify],
    )

    worker_task = asyncio.create_task(worker.run())
    workflow_id = f"reminder-py-{zealt_run_id}"

    try:
        result = await client.execute_workflow(
            ReminderWorkflow.run,
            "wake up",
            3,
            id=workflow_id,
            task_queue="reminder-py",
        )
        print(result)
    finally:
        await worker.shutdown()
        await worker_task


if __name__ == "__main__":
    asyncio.run(async_main())
