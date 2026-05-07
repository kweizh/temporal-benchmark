import os
import asyncio
import uuid
from temporalio.client import Client
from workflows import ReminderWorkflow

async def main():
    address = os.getenv("TEMPORAL_ADDRESS")
    namespace = os.getenv("TEMPORAL_NAMESPACE")
    api_key = os.getenv("TEMPORAL_API_KEY")

    if not address or not namespace or not api_key:
        raise ValueError("TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, and TEMPORAL_API_KEY must be set")

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    result = await client.execute_workflow(
        ReminderWorkflow.run,
        args=[2, "Time is up!"],
        id=f"reminder-workflow-{uuid.uuid4()}",
        task_queue="reminder-task-queue",
    )

    print(f"RESULT: {result}")

if __name__ == "__main__":
    asyncio.run(main())
