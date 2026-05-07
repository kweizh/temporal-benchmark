import asyncio
import os
import sys
from temporalio.client import Client
from workflow import MoneyTransferSaga

async def main():
    if len(sys.argv) != 4:
        print("Usage: python run_workflow.py <source_account> <target_account> <amount>")
        sys.exit(1)

    source_account = sys.argv[1]
    target_account = sys.argv[2]
    amount = int(sys.argv[3])

    # Get environment variables
    address = os.getenv("TEMPORAL_ADDRESS")
    namespace = os.getenv("TEMPORAL_NAMESPACE")
    api_key = os.getenv("TEMPORAL_API_KEY")

    if not all([address, namespace, api_key]):
        raise ValueError("Missing required environment variables: TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY")

    # Connect to Temporal Cloud
    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    # Start workflow
    workflow_id = f"money-transfer-{source_account}-{target_account}-{amount}"
    
    print(f"Starting workflow {workflow_id}...")
    try:
        result = await client.execute_workflow(
            MoneyTransferSaga.run,
            args=[source_account, target_account, amount],
            id=workflow_id,
            task_queue="money-transfer-queue",
        )
        print("Workflow completed successfully.")
    except Exception as e:
        print(f"Workflow failed as expected or due to error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
