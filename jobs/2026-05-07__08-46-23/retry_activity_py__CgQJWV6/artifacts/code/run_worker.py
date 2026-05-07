import asyncio
import os
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import RetryWorkflow, failing_activity

async def main():
    address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    api_key = os.getenv("TEMPORAL_API_KEY")

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
    )

    worker = Worker(
        client,
        task_queue="retry-task-queue",
        workflows=[RetryWorkflow],
        activities=[failing_activity],
    )
    print("Worker started on retry-task-queue...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
