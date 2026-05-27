"""Client: starts CounterWorkflow, sends signals/queries, writes result."""

import asyncio
import os

from temporalio.client import Client

from workflow import CounterWorkflow

TASK_QUEUE = "counter-py"
OUTPUT_FILE = "/workspace/counter.out"


async def main() -> None:
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    run_id = os.environ["ZEALT_RUN_ID"]

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
        task_queue=TASK_QUEUE,
    )
    print(f"Started workflow '{workflow_id}'")

    # 2. Send three increment signals: 1, 2, 3
    await handle.signal(CounterWorkflow.increment, 1)
    print("Sent increment(1)")
    await handle.signal(CounterWorkflow.increment, 2)
    print("Sent increment(2)")
    await handle.signal(CounterWorkflow.increment, 3)
    print("Sent increment(3)")

    # 3. Query current count and print it
    count = await handle.query(CounterWorkflow.get_count)
    print(f"Query get_count returned: {count}")

    # 4. Send finish signal
    await handle.signal(CounterWorkflow.finish)
    print("Sent finish signal")

    # 5. Wait for workflow result and write output file
    result = await handle.result()
    print(f"Workflow completed with result: {result}")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(f"final={result}\n")
    print(f"Written '{OUTPUT_FILE}': final={result}")


if __name__ == "__main__":
    asyncio.run(main())
