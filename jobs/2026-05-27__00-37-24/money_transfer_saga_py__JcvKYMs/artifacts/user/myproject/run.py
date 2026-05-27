import asyncio
import os
import sys
from temporalio.client import Client
from temporalio.worker import Worker
from activities import withdraw, deposit, refund
from workflow import MoneyTransferWorkflow

async def main():
    # Environment variables
    temporal_address = os.getenv("TEMPORAL_ADDRESS")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE")
    temporal_api_key = os.getenv("TEMPORAL_API_KEY")
    run_id = os.getenv("ZEALT_RUN_ID")

    if not all([temporal_address, temporal_namespace, temporal_api_key, run_id]):
        print("Missing required environment variables")
        sys.exit(1)

    task_queue = f"saga-py-{run_id}"
    ok_workflow_id = f"saga-ok-py-{run_id}"
    fail_workflow_id = f"saga-fail-py-{run_id}"
    log_file = "/home/user/myproject/output.log"

    # Connect to Temporal Cloud
    client = await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=True,
    )

    # Start Worker
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[MoneyTransferWorkflow],
        activities=[withdraw, deposit, refund],
    )
    
    # Run worker in background
    worker_task = asyncio.create_task(worker.run())

    try:
        # First Run: A -> B, amount 30 (Success)
        print(f"Starting first workflow: {ok_workflow_id}")
        await client.execute_workflow(
            MoneyTransferWorkflow.run,
            args=["A", "B", 30],
            id=ok_workflow_id,
            task_queue=task_queue,
        )
        print(f"First workflow completed: {ok_workflow_id}")

        # Second Run: A -> B_FAIL, amount 50 (Failure)
        print(f"Starting second workflow: {fail_workflow_id}")
        try:
            await client.execute_workflow(
                MoneyTransferWorkflow.run,
                args=["A", "B_FAIL", 50],
                id=fail_workflow_id,
                task_queue=task_queue,
            )
        except Exception as e:
            print(f"Second workflow failed as expected: {str(e)}")

        # Write to log file
        with open(log_file, "w") as f:
            f.write(f"OK_WORKFLOW_ID: {ok_workflow_id}\n")
            f.write(f"FAIL_WORKFLOW_ID: {fail_workflow_id}\n")

    finally:
        # Shutdown worker
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
