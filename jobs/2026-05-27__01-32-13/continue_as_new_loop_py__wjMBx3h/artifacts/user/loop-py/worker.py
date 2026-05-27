import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from activities import increment_counter
from workflow import LongLoopWorkflow


async def main() -> None:
    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        tls=True,
        api_key=os.environ["TEMPORAL_API_KEY"],
    )

    worker = Worker(
        client,
        task_queue="loop-py",
        workflows=[LongLoopWorkflow],
        activities=[increment_counter],
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
