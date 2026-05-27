import asyncio
import os
from datetime import timedelta

import httpx
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

TASK_QUEUE = "fetch-url-py"


@activity.defn(name="fetch_data")
async def fetch_data(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


@workflow.defn(name="FetchUrlWorkflow")
class FetchUrlWorkflow:
    @workflow.run
    async def run(self) -> str:
        return await workflow.execute_activity(
            fetch_data,
            "https://api.github.com/zen",
            start_to_close_timeout=timedelta(seconds=30),
        )


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


async def main() -> None:
    api_key = _get_env("TEMPORAL_API_KEY")
    address = _get_env("TEMPORAL_ADDRESS")
    namespace = _get_env("TEMPORAL_NAMESPACE")
    run_id = _get_env("ZEALT_RUN_ID")

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[FetchUrlWorkflow],
        activities=[fetch_data],
    )

    worker_task = asyncio.create_task(worker.run())
    try:
        result = await client.execute_workflow(
            FetchUrlWorkflow.run,
            id=f"fetch-wf-{run_id}",
            task_queue=TASK_QUEUE,
        )
        print(result)
    finally:
        await worker.shutdown()
        await worker_task


if __name__ == "__main__":
    asyncio.run(main())
