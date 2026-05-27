from __future__ import annotations

import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from activities import flaky_task
from workflows import FlakyWorkflow


async def main() -> None:
    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )

    worker = Worker(
        client,
        task_queue="retry-py",
        workflows=[FlakyWorkflow],
        activities=[flaky_task],
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
