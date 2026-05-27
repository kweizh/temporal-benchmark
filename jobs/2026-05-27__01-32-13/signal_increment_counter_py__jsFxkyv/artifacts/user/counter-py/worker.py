import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from workflows import CounterWorkflow


async def main() -> None:
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    worker = Worker(
        client,
        task_queue="counter-py",
        workflows=[CounterWorkflow],
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
