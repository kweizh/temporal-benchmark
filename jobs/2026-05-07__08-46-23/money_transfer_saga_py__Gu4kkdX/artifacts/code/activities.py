from temporalio import activity
import os

LOG_FILE = "/home/user/app/transactions.log"

@activity.defn
async def withdraw(account_id: str, amount: int) -> None:
    with open(LOG_FILE, "a") as f:
        f.write(f"WITHDRAW {account_id} {amount}\n")

@activity.defn
async def deposit(account_id: str, amount: int) -> None:
    if account_id == "B_FAIL":
        raise ValueError("Deposit failed")
    with open(LOG_FILE, "a") as f:
        f.write(f"DEPOSIT {account_id} {amount}\n")

@activity.defn
async def refund(account_id: str, amount: int) -> None:
    with open(LOG_FILE, "a") as f:
        f.write(f"REFUND {account_id} {amount}\n")
