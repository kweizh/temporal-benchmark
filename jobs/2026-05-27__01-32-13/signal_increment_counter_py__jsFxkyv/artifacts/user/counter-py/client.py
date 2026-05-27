import asyncio
import os

from temporalio.client import Client

from workflows import CounterWorkflow


async def main() -> None:
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    run_id = os.environ.get("ZEALT_RUN_ID", "local")

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    workflow_id = f"counter-{run_id}"
    handle = await client.start_workflow(
        CounterWorkflow.run,
        id=workflow_id,
        task_queue="counter-py",
    )

    await handle.signal(CounterWorkflow.increment, 1)
    await handle.signal(CounterWorkflow.increment, 2)
    await handle.signal(CounterWorkflow.increment, 3)

    count = await handle.query(CounterWorkflow.get_count)
    print(count)

    await handle.signal(CounterWorkflow.finish)
    result = await handle.result()

    with open("/workspace/counter.out", "w", encoding="utf-8") as output_file:
        output_file.write(f"final={result}\n")


if __name__ == "__main__":
    asyncio.run(main())
