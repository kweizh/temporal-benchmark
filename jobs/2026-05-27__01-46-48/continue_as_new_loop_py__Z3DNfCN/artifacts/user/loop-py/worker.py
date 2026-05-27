import asyncio
import os

from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker

from activities import increment_counter
from workflow import LongLoopWorkflow

TASK_QUEUE = "loop-py"


async def main() -> None:
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]

    client = await Client.connect(
        address,
        namespace=namespace,
        tls=True,
        rpc_metadata={"temporal-namespace": namespace},
        api_key=api_key,
    )

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[LongLoopWorkflow],
        activities=[increment_counter],
    )

    print(f"Worker started on task queue '{TASK_QUEUE}'")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
