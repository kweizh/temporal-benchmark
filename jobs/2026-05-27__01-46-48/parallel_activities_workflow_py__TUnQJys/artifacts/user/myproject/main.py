"""
Entrypoint: starts a Worker (background) and a Client in the same event loop,
executes ParallelFetchWorkflow against Temporal Cloud, prints the result.
"""

import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from activities import fetch_url
from workflows import ParallelFetchWorkflow


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable {name!r} is not set.")
    return value


async def _run() -> None:
    address = _require_env("TEMPORAL_ADDRESS")
    namespace = _require_env("TEMPORAL_NAMESPACE")
    api_key = _require_env("TEMPORAL_API_KEY")
    run_id = _require_env("ZEALT_RUN_ID")

    workflow_id = f"parallel-{run_id}"
    task_queue = "parallel-py"
    urls = [
        "https://www.example.com",
        "https://api.github.com",
        "https://httpbin.org/status/200",
    ]

    # Single shared connection for both worker and client.
    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    # The Worker runs as an async context manager; while it is active the
    # client can drive the workflow. The Worker stops cleanly when the
    # `async with` block exits.
    async with Worker(
        client,
        task_queue=task_queue,
        workflows=[ParallelFetchWorkflow],
        activities=[fetch_url],
    ):
        result: dict[str, int] = await client.execute_workflow(
            ParallelFetchWorkflow.run,
            urls,
            id=workflow_id,
            task_queue=task_queue,
        )

    print(result)


if __name__ == "__main__":
    asyncio.run(_run())
