import asyncio
import os

from temporalio.client import Client

from workflow import LongLoopWorkflow

TASK_QUEUE = "loop-py"


async def main() -> None:
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    run_id = os.environ["ZEALT_RUN_ID"]

    workflow_id = f"loop-py-{run_id}"

    client = await Client.connect(
        address,
        namespace=namespace,
        tls=True,
        rpc_metadata={"temporal-namespace": namespace},
        api_key=api_key,
    )

    print(f"Starting workflow '{workflow_id}' on task queue '{TASK_QUEUE}'")
    result = await client.execute_workflow(
        LongLoopWorkflow.run,
        args=[0, 25],
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )

    print(f"Workflow completed with result: {result}")

    os.makedirs("/workspace", exist_ok=True)
    with open("/workspace/loop.out", "w") as f:
        f.write(f"result={result}\n")

    print("Result written to /workspace/loop.out")


if __name__ == "__main__":
    asyncio.run(main())
