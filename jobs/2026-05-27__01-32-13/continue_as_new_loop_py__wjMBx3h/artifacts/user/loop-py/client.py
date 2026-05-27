import asyncio
import os

from temporalio.client import Client

from workflow import LongLoopWorkflow


async def main() -> None:
    run_id = os.environ.get("ZEALT_RUN_ID", "local")
    workflow_id = f"loop-py-{run_id}"

    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        tls=True,
        api_key=os.environ["TEMPORAL_API_KEY"],
    )

    result = await client.execute_workflow(
        LongLoopWorkflow.run,
        0,
        25,
        id=workflow_id,
        task_queue="loop-py",
    )

    with open("/workspace/loop.out", "w", encoding="utf-8") as output_file:
        output_file.write(f"result={result}")


if __name__ == "__main__":
    asyncio.run(main())
