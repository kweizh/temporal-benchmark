import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from activities import fetch_data
from workflows import FetchUrlWorkflow


async def main() -> None:
    run_id = os.environ["ZEALT_RUN_ID"]
    workflow_id = f"fetch-wf-{run_id}"
    task_queue = "fetch-url-py"

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
        task_queue=task_queue,
        workflows=[FetchUrlWorkflow],
        activities=[fetch_data],
    )

    # Run the worker as a background context manager, execute the workflow,
    # then the 'async with' block exits and the worker shuts down cleanly.
    async with worker:
        result: str = await client.execute_workflow(
            FetchUrlWorkflow.run,
            id=workflow_id,
            task_queue=task_queue,
        )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
