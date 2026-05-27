import asyncio
import os
from temporalio.client import Client
from workflow import CounterWorkflow

async def main():
    address = os.environ.get("TEMPORAL_ADDRESS")
    namespace = os.environ.get("TEMPORAL_NAMESPACE")
    api_key = os.environ.get("TEMPORAL_API_KEY")
    run_id = os.environ.get("ZEALT_RUN_ID", "default")
    
    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True
    )
    
    workflow_id = f"counter-{run_id}"

    # Start the workflow
    handle = await client.start_workflow(
        CounterWorkflow.run,
        id=workflow_id,
        task_queue="counter-py"
    )

    # Send signals
    await handle.signal(CounterWorkflow.increment, 1)
    await handle.signal(CounterWorkflow.increment, 2)
    await handle.signal(CounterWorkflow.increment, 3)

    # Query
    count = await handle.query(CounterWorkflow.get_count)
    print(f"Current count: {count}")

    # Finish
    await handle.signal(CounterWorkflow.finish)

    # Wait for result
    final_count = await handle.result()
    print(f"Final count: {final_count}")

    with open("/workspace/counter.out", "w") as f:
        f.write(f"final={final_count}\n")

if __name__ == "__main__":
    asyncio.run(main())
