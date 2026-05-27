import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from activities import flaky_task
from workflows import FlakyWorkflow

TASK_QUEUE = "retry-py"


async def main() -> None:
    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[FlakyWorkflow],
        activities=[flaky_task],
    )

    print("Worker started, polling task queue:", TASK_QUEUE)
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
