import json
import os
from temporalio import activity
from temporalio.exceptions import ApplicationError

ACCOUNTS_FILE = "/workspace/accounts.json"

def _read_accounts():
    with open(ACCOUNTS_FILE, "r") as f:
        return json.load(f)

def _write_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=2)

@activity.defn
async def withdraw(from_account: str, amount: int):
    accounts = _read_accounts()
    if accounts.get(from_account, 0) < amount:
        raise ApplicationError(f"Insufficient funds in {from_account}")
    accounts[from_account] -= amount
    _write_accounts(accounts)
    return f"Withdrew {amount} from {from_account}"

@activity.defn
async def deposit(to_account: str, amount: int):
    if to_account == "B_FAIL":
        raise ApplicationError("Simulated deposit failure", non_retryable=True)
    
    accounts = _read_accounts()
    accounts[to_account] = accounts.get(to_account, 0) + amount
    _write_accounts(accounts)
    return f"Deposited {amount} to {to_account}"

@activity.defn
async def refund(from_account: str, amount: int):
    accounts = _read_accounts()
    accounts[from_account] = accounts.get(from_account, 0) + amount
    _write_accounts(accounts)
    return f"Refunded {amount} to {from_account}"
