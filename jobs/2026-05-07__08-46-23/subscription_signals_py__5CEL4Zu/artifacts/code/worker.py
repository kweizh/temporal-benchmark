import asyncio
import os
import logging
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import SubscriptionWorkflow

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    # Get environment variables
    server_address = os.getenv("TEMPORAL_ADDRESS")
    namespace = os.getenv("TEMPORAL_NAMESPACE")
    api_key = os.getenv("TEMPORAL_API_KEY")

    if not all([server_address, namespace, api_key]):
        logging.error("Missing required environment variables: TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY")
        return

    # Connect to Temporal Cloud
    try:
        client = await Client.connect(
            server_address,
            namespace=namespace,
            api_key=api_key,
        )
        logging.info(f"Connected to Temporal Cloud at {server_address}")
    except Exception as e:
        logging.error(f"Failed to connect to Temporal: {e}")
        return

    # Run the worker
    worker = Worker(
        client,
        task_queue="subscription-task-queue",
        workflows=[SubscriptionWorkflow],
    )
    logging.info("Worker started on task queue 'subscription-task-queue'")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
