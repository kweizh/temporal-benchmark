import asyncio
import os
from temporalio.client import Client
from workflow import LongLoopWorkflow

async def main():
    address = os.getenv("TEMPORAL_ADDRESS")
    namespace = os.getenv("TEMPORAL_NAMESPACE")
    api_key = os.getenv("TEMPORAL_API_KEY")
    zealt_run_id = os.getenv("ZEALT_RUN_ID")
    
    workflow_id = f"loop-py-{zealt_run_id}"

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    print(f"Starting or attaching to workflow {workflow_id}...")
    try:
        handle = await client.start_workflow(
            LongLoopWorkflow.run,
            args=[0, 25],
            id=workflow_id,
            task_queue="loop-py",
        )
    except Exception as e:
        print(f"Workflow already started, attaching to {workflow_id}...")
        handle = client.get_workflow_handle(workflow_id)
    
    result = await handle.result()

    workspace_path = "/workspace"
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)
        
    output_file = os.path.join(workspace_path, "loop.out")
    with open(output_file, "w") as f:
        f.write(f"result={result}\n")
    
    print(f"Workflow completed with result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
