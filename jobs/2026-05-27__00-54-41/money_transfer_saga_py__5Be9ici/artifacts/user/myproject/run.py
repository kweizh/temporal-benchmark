import asyncio
import json
import os
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.exceptions import ApplicationError, ActivityError

ACCOUNTS_FILE = "/workspace/accounts.json"

def read_accounts():
    with open(ACCOUNTS_FILE, "r") as f:
        return json.load(f)

def write_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f)

@activity.defn
def withdraw(from_account: str, amount: int):
    accounts = read_accounts()
    if from_account not in accounts:
        accounts[from_account] = 0
    accounts[from_account] -= amount
    write_accounts(accounts)
    return True

@activity.defn
def deposit(to_account: str, amount: int):
    if to_account == "B_FAIL":
        raise ApplicationError("Simulated deposit failure", non_retryable=True)
    
    accounts = read_accounts()
    if to_account not in accounts:
        accounts[to_account] = 0
    accounts[to_account] += amount
    write_accounts(accounts)
    return True

@activity.defn
def refund(from_account: str, amount: int):
    accounts = read_accounts()
    if from_account not in accounts:
        accounts[from_account] = 0
    accounts[from_account] += amount
    write_accounts(accounts)
    return True

@workflow.defn
class MoneyTransferWorkflow:
    @workflow.run
    async def run(self, from_account: str, to_account: str, amount: int):
        await workflow.execute_activity(
            withdraw,
            args=[from_account, amount],
            start_to_close_timeout=timedelta(seconds=10),
        )

        try:
            await workflow.execute_activity(
                deposit,
                args=[to_account, amount],
                start_to_close_timeout=timedelta(seconds=10),
            )
        except ActivityError as e:
            await workflow.execute_activity(
                refund,
                args=[from_account, amount],
                start_to_close_timeout=timedelta(seconds=10),
            )
            raise ApplicationError("Workflow failed due to deposit failure", non_retryable=True)

async def main():
    # Initialize accounts
    write_accounts({
        "A": 100,
        "B": 0,
        "B_FAIL": 0
    })

    temporal_address = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
    temporal_namespace = os.environ.get("TEMPORAL_NAMESPACE", "default")
    temporal_api_key = os.environ.get("TEMPORAL_API_KEY", "")
    run_id = os.environ.get("ZEALT_RUN_ID", "default-run-id")

    task_queue = f"saga-py-{run_id}"
    ok_workflow_id = f"saga-ok-py-{run_id}"
    fail_workflow_id = f"saga-fail-py-{run_id}"

    # Connect client
    tls = True if "tmprl.cloud" in temporal_address else False
    
    client = await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=tls,
    )

    # Start worker
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[MoneyTransferWorkflow],
        activities=[withdraw, deposit, refund],
    )
    
    worker_task = asyncio.create_task(worker.run())

    try:
        # Run OK workflow
        await client.execute_workflow(
            MoneyTransferWorkflow.run,
            "A", "B", 30,
            id=ok_workflow_id,
            task_queue=task_queue,
        )

        # Run FAIL workflow
        try:
            await client.execute_workflow(
                MoneyTransferWorkflow.run,
                "A", "B_FAIL", 50,
                id=fail_workflow_id,
                task_queue=task_queue,
            )
        except Exception as e:
            print(f"Expected failure caught: {e}")

        # Write to output.log
        with open("/home/user/myproject/output.log", "w") as f:
            f.write(f"OK_WORKFLOW_ID: {ok_workflow_id}\n")
            f.write(f"FAIL_WORKFLOW_ID: {fail_workflow_id}\n")

    finally:
        # Stop worker
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())