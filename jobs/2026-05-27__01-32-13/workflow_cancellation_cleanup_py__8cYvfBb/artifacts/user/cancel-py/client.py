from __future__ import annotations

import asyncio
import os

from temporalio.client import Client, WorkflowFailureError
from temporalio.exceptions import CancelledError

from workflows import LongJobWorkflow


async def main() -> None:
    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )

    workflow_id = f"job-{os.environ['ZEALT_RUN_ID']}"
    handle = await client.start_workflow(
        LongJobWorkflow.run,
        "alpha",
        id=workflow_id,
        task_queue="cancel-py",
    )

    await asyncio.sleep(3)
    await handle.cancel()

    try:
        await handle.result()
    except WorkflowFailureError as exc:
        if isinstance(exc.cause, CancelledError):
            return
        raise


if __name__ == "__main__":
    asyncio.run(main())
