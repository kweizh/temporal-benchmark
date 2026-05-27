from __future__ import annotations

import asyncio
import os

from temporalio.client import Client

from workflow import StatefulWorkflow


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


async def main() -> None:
    run_id = _get_env("ZEALT_RUN_ID")
    address = _get_env("TEMPORAL_ADDRESS")
    namespace = _get_env("TEMPORAL_NAMESPACE")
    api_key = _get_env("TEMPORAL_API_KEY")

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    workflow_id = f"query-wf-{run_id}"
    handle = await client.start_workflow(
        StatefulWorkflow.run,
        id=workflow_id,
        task_queue="query-handler-py",
    )

    await asyncio.sleep(2)

    mid_counter = await handle.query(StatefulWorkflow.get_counter)
    await handle.signal(StatefulWorkflow.finish)
    final_counter = await handle.result()

    print(f"Mid counter: {mid_counter}")
    print(f"Final counter: {final_counter}")


if __name__ == "__main__":
    asyncio.run(main())
