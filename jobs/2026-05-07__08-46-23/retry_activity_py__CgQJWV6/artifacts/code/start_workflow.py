import asyncio
import os
from temporalio.client import Client
from workflow import RetryWorkflow

async def main():
    address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    api_key = os.getenv("TEMPORAL_API_KEY")

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
    )

    result = await client.execute_workflow(
        RetryWorkflow.run,
        id="retry-workflow-id",
        task_queue="retry-task-queue",
    )

    print(f"Workflow result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
