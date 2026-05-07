import asyncio
import os
from temporalio.client import Client
from temporalio.worker import Worker
from activities import withdraw, deposit, refund
from workflow import MoneyTransferSaga

async def main():
    # Get environment variables
    address = os.getenv("TEMPORAL_ADDRESS")
    namespace = os.getenv("TEMPORAL_NAMESPACE")
    api_key = os.getenv("TEMPORAL_API_KEY")

    if not all([address, namespace, api_key]):
        raise ValueError("Missing required environment variables: TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY")

    # Connect to Temporal Cloud
    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    # Create worker
    worker = Worker(
        client,
        task_queue="money-transfer-queue",
        workflows=[MoneyTransferSaga],
        activities=[withdraw, deposit, refund],
    )

    print("Worker started...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
