import asyncio
import os

from temporalio.client import Client

from workflows import FlakyWorkflow

TASK_QUEUE = "retry-py"


async def main() -> None:
    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )

    run_id = os.environ["ZEALT_RUN_ID"]
    workflow_id = f"retry-py-{run_id}"

    print(f"Starting workflow with ID: {workflow_id}")
    result = await client.execute_workflow(
        FlakyWorkflow.run,
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )

    print(f"Workflow result: {result}")
    with open("/workspace/result.log", "w") as f:
        f.write(f"Workflow result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())
