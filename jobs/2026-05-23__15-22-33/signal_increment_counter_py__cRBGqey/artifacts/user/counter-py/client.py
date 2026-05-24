import asyncio
import os
from temporalio.client import Client
from workflow import CounterWorkflow

async def main():
    address = os.getenv("TEMPORAL_ADDRESS")
    namespace = os.getenv("TEMPORAL_NAMESPACE")
    api_key = os.getenv("TEMPORAL_API_KEY")
    run_id = os.getenv("ZEALT_RUN_ID")
    workflow_id = f"counter-{run_id}"

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    # 1. Start the CounterWorkflow
    handle = await client.start_workflow(
        CounterWorkflow.run,
        id=workflow_id,
        task_queue="counter-py",
    )

    # 2. Send three increment Signals (1, 2, 3)
    await handle.signal(CounterWorkflow.increment, 1)
    await handle.signal(CounterWorkflow.increment, 2)
    await handle.signal(CounterWorkflow.increment, 3)

    # 3. Send a get_count Query and print the returned value
    count = await handle.query(CounterWorkflow.get_count)
    print(f"Current count: {count}")

    # 4. Send a finish Signal
    await handle.signal(CounterWorkflow.finish)

    # 5. Wait for the workflow result and write to /workspace/counter.out
    result = await handle.result()
    print(f"Final result: {result}")
    
    os.makedirs("/workspace", exist_ok=True)
    with open("/workspace/counter.out", "w") as f:
        f.write(f"final={result}\n")

if __name__ == "__main__":
    asyncio.run(main())
