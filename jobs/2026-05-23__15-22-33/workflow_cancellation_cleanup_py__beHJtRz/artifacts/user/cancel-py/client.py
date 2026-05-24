import asyncio
import os
import sys
from temporalio.client import Client, WorkflowFailureError
from temporalio.exceptions import CancelledError as TemporalCancelledError
from temporalio.api.enums.v1 import WorkflowExecutionStatus

async def main():
    address = os.getenv("TEMPORAL_ADDRESS")
    namespace = os.getenv("TEMPORAL_NAMESPACE")
    api_key = os.getenv("TEMPORAL_API_KEY")
    zealt_run_id = os.getenv("ZEALT_RUN_ID", "default")

    if not all([address, namespace, api_key]):
        print("Missing required environment variables: TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY")
        sys.exit(1)

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    workflow_id = f"job-{zealt_run_id}"
    print(f"Starting workflow: {workflow_id}")
    
    handle = await client.start_workflow(
        "LongJobWorkflow",
        "alpha",
        id=workflow_id,
        task_queue="cancel-py",
    )

    print("Waiting 3 seconds before cancelling...")
    await asyncio.sleep(3)

    print(f"Cancelling workflow: {workflow_id}")
    await handle.cancel()

    try:
        await handle.result()
        print("Workflow completed successfully (unexpectedly)")
        sys.exit(1)
    except WorkflowFailureError as e:
        print(f"Workflow failed with error: {e}")
        print(f"Cause: {type(e.cause)}: {e.cause}")
        # Check if the cause is cancellation
        if isinstance(e.cause, (asyncio.CancelledError, TemporalCancelledError)) or "CancelledError" in str(e) or "Canceled" in str(e):
            print("Workflow confirmed as cancelled.")
            
            # Verify status on server
            desc = await handle.describe()
            if desc.status == WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_CANCELED:
                print("Server status is CANCELED.")
                sys.exit(0)
            else:
                print(f"Server status is {desc.status}, expected CANCELED.")
                sys.exit(1)
        else:
            print(f"Workflow failed with unexpected error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
