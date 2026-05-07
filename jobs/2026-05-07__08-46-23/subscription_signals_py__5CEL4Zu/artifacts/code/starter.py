import asyncio
import os
import uuid
import logging
from temporalio.client import Client
from workflow import SubscriptionWorkflow

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    # Get environment variables
    server_address = os.getenv("TEMPORAL_ADDRESS")
    namespace = os.getenv("TEMPORAL_NAMESPACE")
    api_key = os.getenv("TEMPORAL_API_KEY")

    if not all([server_address, namespace, api_key]):
        logging.error("Missing required environment variables: TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY")
        return

    # Connect to Temporal Cloud
    try:
        client = await Client.connect(
            server_address,
            namespace=namespace,
            api_key=api_key,
        )
    except Exception as e:
        logging.error(f"Failed to connect to Temporal: {e}")
        return

    workflow_id = f"subscription-workflow-{uuid.uuid4()}"

    # Start the workflow
    logging.info(f"Starting workflow with ID: {workflow_id}")
    handle = await client.start_workflow(
        SubscriptionWorkflow.run,
        id=workflow_id,
        task_queue="subscription-task-queue",
    )

    # Wait a bit to simulate time passing before signal
    await asyncio.sleep(5)
    
    # Send upgrade signal
    logging.info("Sending upgrade signal: premium")
    await handle.signal(SubscriptionWorkflow.upgrade, "premium")

    # Wait a bit more
    await asyncio.sleep(5)

    # Send cancel signal
    logging.info("Sending cancel signal")
    await handle.signal(SubscriptionWorkflow.cancel)

    # Wait for result
    result = await handle.result()
    logging.info(f"Workflow result: {result}")
    print(f"FINAL_RESULT: {result}")

if __name__ == "__main__":
    asyncio.run(main())
