from __future__ import annotations

import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from activities import release_resources
from workflows import LongJobWorkflow


async def main() -> None:
    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )

    worker = Worker(
        client,
        task_queue="cancel-py",
        workflows=[LongJobWorkflow],
        activities=[release_resources],
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
