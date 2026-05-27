"""Worker: polls task queue 'counter-py' and hosts CounterWorkflow."""

import asyncio
import os

from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker

from workflow import CounterWorkflow

TASK_QUEUE = "counter-py"


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
        workflows=[CounterWorkflow],
        activities=[],
    )

    print(f"Worker started, polling task queue '{TASK_QUEUE}'...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
