import asyncio
import os
from temporalio.client import Client
from workflow import LongLoopWorkflow

async def main():
    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )
    run_id = os.environ.get("ZEALT_RUN_ID", "default")
    workflow_id = f"loop-py-{run_id}"
    
    try:
        result = await client.execute_workflow(
            LongLoopWorkflow.run,
            args=[0, 25],
            id=workflow_id,
            task_queue="loop-py",
        )
    except Exception:
        handle = client.get_workflow_handle(workflow_id)
        result = await handle.result()
    
    with open("/workspace/loop.out", "w") as f:
        f.write(f"result={result}\n")

if __name__ == "__main__":
    asyncio.run(main())
