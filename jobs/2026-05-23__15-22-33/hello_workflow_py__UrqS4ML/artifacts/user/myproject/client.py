import asyncio
import os
from temporalio.client import Client
from workflows import HelloWorkflow

async def main():
    # Read environment variables
    address = os.environ.get("TEMPORAL_ADDRESS")
    namespace = os.environ.get("TEMPORAL_NAMESPACE")
    api_key = os.environ.get("TEMPORAL_API_KEY")
    run_id = os.environ.get("ZEALT_RUN_ID", "default")

    if not all([address, namespace, api_key]):
        raise ValueError("Missing required environment variables: TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY")

    # Connect to Temporal Cloud
    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    # Execute workflow
    workflow_id = f"hello-py-{run_id}"
    result = await client.execute_workflow(
        HelloWorkflow.run,
        "Temporal",
        id=workflow_id,
        task_queue="hello-world-py",
    )

    print(result)

if __name__ == "__main__":
    asyncio.run(main())
