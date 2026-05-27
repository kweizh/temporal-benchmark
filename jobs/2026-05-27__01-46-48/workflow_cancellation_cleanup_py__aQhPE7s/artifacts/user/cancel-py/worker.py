"""Temporal worker that polls the 'cancel-py' task queue."""

import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from activities import release_resources
from workflows import LongJobWorkflow

TASK_QUEUE = "cancel-py"


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
        task_queue=TASK_QUEUE,
        workflows=[LongJobWorkflow],
        activities=[release_resources],
    )

    print(f"Worker started, polling task queue '{TASK_QUEUE}'")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
