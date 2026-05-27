import asyncio
import json
import os

from temporalio.client import Client

TASK_QUEUE = "discount-py"
LOG_FILE = "/home/user/discount-py/output.log"


async def main():
    run_id = os.environ["ZEALT_RUN_ID"]
    workflow_id = f"discount-py-{run_id}"

    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )

    result = await client.execute_workflow(
        "DiscountWorkflow",
        "user-42",
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )

    with open(LOG_FILE, "w") as f:
        f.write(f"Workflow result: {json.dumps(result)}\n")

    print(f"Workflow result: {json.dumps(result)}")


if __name__ == "__main__":
    asyncio.run(main())
