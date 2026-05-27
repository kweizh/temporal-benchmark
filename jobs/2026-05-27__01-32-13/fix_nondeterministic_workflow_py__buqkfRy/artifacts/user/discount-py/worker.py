import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from activities import pick_discount
from workflows import DiscountWorkflow

TASK_QUEUE = "discount-py"


async def main():
    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[DiscountWorkflow],
        activities=[pick_discount],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
