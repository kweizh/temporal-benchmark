import asyncio
import os
import sys
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import LongJobWorkflow, release_resources

async def main():
    address = os.getenv("TEMPORAL_ADDRESS")
    namespace = os.getenv("TEMPORAL_NAMESPACE")
    api_key = os.getenv("TEMPORAL_API_KEY")

    if not all([address, namespace, api_key]):
        print("Missing required environment variables: TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY")
        sys.exit(1)

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    worker = Worker(
        client,
        task_queue="cancel-py",
        workflows=[LongJobWorkflow],
        activities=[release_resources],
    )
    
    print("Worker started on task queue 'cancel-py'...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
