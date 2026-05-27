import asyncio
import os
from contextlib import suppress
from datetime import timedelta

import httpx
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

TASK_QUEUE = "parallel-py"


@activity.defn
async def fetch_url(url: str) -> int:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return int(response.status_code)


@workflow.defn
class ParallelFetchWorkflow:
    @workflow.run
    async def run(self, urls: list[str]) -> dict[str, int]:
        tasks = [
            workflow.execute_activity(
                fetch_url,
                url,
                start_to_close_timeout=timedelta(seconds=30),
            )
            for url in urls
        ]
        results = await asyncio.gather(*tasks)
        return dict(zip(urls, results))


async def run_workflow() -> None:
    temporal_api_key = os.environ["TEMPORAL_API_KEY"]
    temporal_address = os.environ["TEMPORAL_ADDRESS"]
    temporal_namespace = os.environ["TEMPORAL_NAMESPACE"]
    run_id = os.environ["ZEALT_RUN_ID"]

    client = await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=True,
    )

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ParallelFetchWorkflow],
        activities=[fetch_url],
    )

    worker_task = asyncio.create_task(worker.run())
    try:
        urls = [
            "https://www.example.com",
            "https://api.github.com",
            "https://httpbin.org/status/200",
        ]
        workflow_id = f"parallel-{run_id}"
        result = await client.execute_workflow(
            ParallelFetchWorkflow.run,
            urls,
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )
        print(result)
    finally:
        worker_task.cancel()
        with suppress(asyncio.CancelledError):
            await worker_task


def main() -> None:
    asyncio.run(run_workflow())


if __name__ == "__main__":
    main()
