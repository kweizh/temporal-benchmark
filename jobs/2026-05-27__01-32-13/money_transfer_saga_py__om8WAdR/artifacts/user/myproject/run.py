import asyncio
import json
import os
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.exceptions import ActivityError, ApplicationError
from temporalio.worker import Worker

ACCOUNTS_PATH = "/workspace/accounts.json"
LOG_PATH = "/home/user/myproject/output.log"


def _read_accounts() -> dict:
    with open(ACCOUNTS_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_accounts(accounts: dict) -> None:
    with open(ACCOUNTS_PATH, "w", encoding="utf-8") as handle:
        json.dump(accounts, handle)


@activity.defn
def withdraw(from_account: str, amount: int) -> None:
    accounts = _read_accounts()
    accounts.setdefault(from_account, 0)
    accounts[from_account] -= amount
    _write_accounts(accounts)


@activity.defn
def deposit(to_account: str, amount: int) -> None:
    if to_account == "B_FAIL":
        raise ApplicationError("Deposit failed", non_retryable=True)
    accounts = _read_accounts()
    accounts.setdefault(to_account, 0)
    accounts[to_account] += amount
    _write_accounts(accounts)


@activity.defn
def refund(from_account: str, amount: int) -> None:
    accounts = _read_accounts()
    accounts.setdefault(from_account, 0)
    accounts[from_account] += amount
    _write_accounts(accounts)


@workflow.defn
class MoneyTransferWorkflow:
    @workflow.run
    async def run(self, from_account: str, to_account: str, amount: int) -> None:
        await workflow.execute_activity(
            withdraw,
            from_account,
            amount,
            start_to_close_timeout=timedelta(seconds=10),
        )
        try:
            await workflow.execute_activity(
                deposit,
                to_account,
                amount,
                start_to_close_timeout=timedelta(seconds=10),
            )
        except ActivityError as exc:
            await workflow.execute_activity(
                refund,
                from_account,
                amount,
                start_to_close_timeout=timedelta(seconds=10),
            )
            raise ApplicationError("Deposit failed; refund issued", non_retryable=True) from exc


def _ensure_initial_accounts() -> None:
    accounts = _read_accounts()
    accounts.setdefault("A", 100)
    accounts.setdefault("B", 0)
    accounts.setdefault("B_FAIL", 0)
    _write_accounts(accounts)


async def main() -> None:
    run_id = os.environ.get("ZEALT_RUN_ID")
    if not run_id:
        raise RuntimeError("ZEALT_RUN_ID is required")

    address = os.environ.get("TEMPORAL_ADDRESS")
    namespace = os.environ.get("TEMPORAL_NAMESPACE")
    api_key = os.environ.get("TEMPORAL_API_KEY")
    if not address or not namespace or not api_key:
        raise RuntimeError("TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY are required")

    task_queue = f"saga-py-{run_id}"
    ok_workflow_id = f"saga-ok-py-{run_id}"
    fail_workflow_id = f"saga-fail-py-{run_id}"

    with open(LOG_PATH, "w", encoding="utf-8") as log_handle:
        log_handle.write(f"OK_WORKFLOW_ID: {ok_workflow_id}\n")
        log_handle.write(f"FAIL_WORKFLOW_ID: {fail_workflow_id}\n")

    _ensure_initial_accounts()

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    async with Worker(
        client,
        task_queue=task_queue,
        workflows=[MoneyTransferWorkflow],
        activities=[withdraw, deposit, refund],
    ):
        await client.execute_workflow(
            MoneyTransferWorkflow.run,
            "A",
            "B",
            30,
            id=ok_workflow_id,
            task_queue=task_queue,
        )

        try:
            await client.execute_workflow(
                MoneyTransferWorkflow.run,
                "A",
                "B_FAIL",
                50,
                id=fail_workflow_id,
                task_queue=task_queue,
            )
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
