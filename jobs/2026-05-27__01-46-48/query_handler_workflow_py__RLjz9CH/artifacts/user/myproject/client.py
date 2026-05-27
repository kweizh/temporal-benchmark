"""Client entrypoint: starts the workflow, issues a mid-run query,
sends the finish signal, awaits the result, and prints both lines."""

import asyncio
import os

from temporalio.client import Client

from workflow import StatefulWorkflow

TASK_QUEUE = "query-handler-py"


async def main() -> None:
    run_id = os.environ["ZEALT_RUN_ID"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]

    workflow_id = f"query-wf-{run_id}"

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    # Start the workflow
    handle = await client.start_workflow(
        StatefulWorkflow.run,
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )

    # Wait ~2 seconds so the counter has been incremented at least once
    await asyncio.sleep(2)

    # Mid-run query: observe the in-flight counter value
    mid_counter: int = await handle.query(StatefulWorkflow.get_counter)
    print(f"Mid counter: {mid_counter}", flush=True)

    # Send finish signal so the workflow exits cleanly
    await handle.signal(StatefulWorkflow.finish)

    # Await the final result
    final_counter: int = await handle.result()
    print(f"Final counter: {final_counter}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
