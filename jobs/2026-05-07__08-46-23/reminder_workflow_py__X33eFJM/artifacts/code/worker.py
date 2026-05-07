import os
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from activities import notify
from workflows import ReminderWorkflow

async def main():
    address = os.getenv("TEMPORAL_ADDRESS")
    namespace = os.getenv("TEMPORAL_NAMESPACE")
    api_key = os.getenv("TEMPORAL_API_KEY")

    if not address or not namespace or not api_key:
        raise ValueError("TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, and TEMPORAL_API_KEY must be set")

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    worker = Worker(
        client,
        task_queue="reminder-task-queue",
        workflows=[ReminderWorkflow],
        activities=[notify],
    )
    print("Worker started on reminder-task-queue")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
