"""
Client script:
  1. Connects to Temporal Cloud.
  2. Starts LongJobWorkflow with id job-<ZEALT_RUN_ID>.
  3. Waits ~3 seconds, then cancels the workflow.
  4. Awaits the result and exits 0 on cancellation (expected outcome).
"""

import asyncio
import os

from temporalio.client import Client, WorkflowFailureError
from temporalio.exceptions import CancelledError as TemporalCancelledError

TASK_QUEUE = "cancel-py"


async def main() -> None:
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    run_id = os.environ["ZEALT_RUN_ID"]
    workflow_id = f"job-{run_id}"

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    # Start the workflow
    handle = await client.start_workflow(
        "LongJobWorkflow",
        "alpha",  # job_id argument
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )
    print(f"Started workflow id={workflow_id}, run_id={handle.result_run_id}")

    # Wait ~3 seconds then cancel
    await asyncio.sleep(3)
    await handle.cancel()
    print("Cancellation requested")

    # Await the result; expect it to be cancelled
    try:
        await handle.result()
        # If we get here without error the workflow succeeded unexpectedly
        print("ERROR: workflow completed without cancellation")
        raise SystemExit(1)
    except WorkflowFailureError as exc:
        # The SDK wraps the server-side CancelledError in a WorkflowFailureError
        if isinstance(exc.cause, TemporalCancelledError):
            print("Workflow successfully cancelled (WorkflowFailureError -> CancelledError)")
        else:
            print(f"ERROR: workflow failed with unexpected cause: {exc.cause!r}")
            raise SystemExit(1)
    except asyncio.CancelledError:
        # Some SDK versions surface this directly
        print("Workflow successfully cancelled (asyncio.CancelledError)")

    print("Client exiting cleanly with status 0")


if __name__ == "__main__":
    asyncio.run(main())
