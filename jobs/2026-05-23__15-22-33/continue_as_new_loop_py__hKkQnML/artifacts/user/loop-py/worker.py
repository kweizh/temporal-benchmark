import asyncio
import os
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import LongLoopWorkflow, increment_counter

async def main():
    address = os.getenv("TEMPORAL_ADDRESS")
    namespace = os.getenv("TEMPORAL_NAMESPACE")
    api_key = os.getenv("TEMPORAL_API_KEY")

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    worker = Worker(
        client,
        task_queue="loop-py",
        workflows=[LongLoopWorkflow],
        activities=[increment_counter],
    )
    
    print("Worker started...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
