"""Worker process that connects to Temporal Cloud and polls the task queue."""

import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from workflow import StatefulWorkflow

TASK_QUEUE = "query-handler-py"


async def main() -> None:
    api_key = os.environ["TEMPORAL_API_KEY"]
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[StatefulWorkflow],
    )

    print(f"Worker started, polling task queue '{TASK_QUEUE}' ...", flush=True)
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
