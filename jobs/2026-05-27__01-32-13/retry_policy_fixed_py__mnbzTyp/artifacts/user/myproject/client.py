from __future__ import annotations

import asyncio
import os

from temporalio.client import Client

from workflows import FlakyWorkflow


async def main() -> None:
    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )

    workflow_id = f"retry-py-{os.environ['ZEALT_RUN_ID']}"
    result = await client.execute_workflow(
        FlakyWorkflow.run,
        id=workflow_id,
        task_queue="retry-py",
    )

    with open("/workspace/result.log", "w", encoding="utf-8") as log_file:
        log_file.write(f"Workflow result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())
