import asyncio
import os
from temporalio.client import Client
from temporalio.worker import Worker
from activities import greet
from workflows import HelloWorkflow

async def main():
    # Read environment variables
    address = os.environ.get("TEMPORAL_ADDRESS")
    namespace = os.environ.get("TEMPORAL_NAMESPACE")
    api_key = os.environ.get("TEMPORAL_API_KEY")

    if not all([address, namespace, api_key]):
        raise ValueError("Missing required environment variables: TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY")

    # Connect to Temporal Cloud
    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    # Run the worker
    worker = Worker(
        client,
        task_queue="hello-world-py",
        workflows=[HelloWorkflow],
        activities=[greet],
    )
    print("Worker started")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
