import asyncio
import os
from temporalio.client import Client

from workflows import FlakyWorkflow

async def main():
    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )
    
    run_id = os.environ.get("ZEALT_RUN_ID", "default")
    workflow_id = f"retry-py-{run_id}"
    
    print(f"Starting workflow {workflow_id}...")
    result = await client.execute_workflow(
        FlakyWorkflow.run,
        id=workflow_id,
        task_queue="retry-py",
    )
    
    with open("/workspace/result.log", "w") as f:
        f.write(f"Workflow result: {result}\n")
    print(f"Workflow completed with result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
