import asyncio
import os
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

@activity.defn
async def notify(message: str) -> str:
    log_path = "/workspace/reminder.log"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    result = f"Notified: {message}"
    with open(log_path, "a") as f:
        f.write(result + "\n")
    return result

@workflow.defn
class ReminderWorkflow:
    @workflow.run
    async def run(self, message: str, delay_seconds: int) -> str:
        await asyncio.sleep(delay_seconds)
        return await workflow.execute_activity(
            notify,
            message,
            start_to_close_timeout=timedelta(seconds=10)
        )

async def main():
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    run_id = os.environ.get("ZEALT_RUN_ID", "default")
    
    # Connect to Temporal Cloud
    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True
    )
    
    # Run a worker
    worker = Worker(
        client,
        task_queue="reminder-py",
        workflows=[ReminderWorkflow],
        activities=[notify]
    )
    
    # Start the worker in the background
    worker_task = asyncio.create_task(worker.run())
    
    # Execute the workflow
    workflow_id = f"reminder-py-{run_id}"
    try:
        result = await client.execute_workflow(
            ReminderWorkflow.run,
            "wake up",
            3,
            id=workflow_id,
            task_queue="reminder-py"
        )
        print(result)
    finally:
        # Stop the worker
        # Using cancel on the task is standard for shutting down an inline worker
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
