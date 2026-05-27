import asyncio
import os
from temporalio.client import Client

async def main():
    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )
    run_id = os.environ.get("ZEALT_RUN_ID", "default")
    workflow_id = f"loop-py-{run_id}"
    
    handle = client.get_workflow_handle(workflow_id)
    try:
        desc = await handle.describe()
        print(f"Status: {desc.status}")
        result = await handle.result()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
