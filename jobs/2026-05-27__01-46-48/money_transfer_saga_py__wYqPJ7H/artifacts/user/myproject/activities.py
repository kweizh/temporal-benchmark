"""
Temporal activities for the Money Transfer Saga.

All activities perform direct file I/O on /workspace/accounts.json.
"""
import asyncio
import json
import os
from temporalio import activity
from temporalio.exceptions import ApplicationError

ACCOUNTS_FILE = "/workspace/accounts.json"
_file_lock = asyncio.Lock()


def _read_accounts() -> dict:
    with open(ACCOUNTS_FILE, "r") as f:
        return json.load(f)


def _write_accounts(data: dict) -> None:
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(data, f, indent=2)


@activity.defn
async def withdraw(from_account: str, amount: int) -> None:
    """Subtract *amount* from *from_account* balance."""
    async with _file_lock:
        accounts = _read_accounts()
        if from_account not in accounts:
            raise ApplicationError(
                f"Account {from_account!r} not found",
                non_retryable=True,
            )
        balance = accounts[from_account]
        if balance < amount:
            raise ApplicationError(
                f"Insufficient funds in {from_account!r}: has {balance}, need {amount}",
                non_retryable=True,
            )
        accounts[from_account] = balance - amount
        _write_accounts(accounts)
        activity.logger.info(
            "Withdrew %d from %s (new balance: %d)",
            amount,
            from_account,
            accounts[from_account],
        )


@activity.defn
async def deposit(to_account: str, amount: int) -> None:
    """Add *amount* to *to_account* balance.

    If *to_account* is ``"B_FAIL"`` the activity raises a non-retryable
    :class:`ApplicationError` so the saga compensation kicks in immediately.
    """
    if to_account == "B_FAIL":
        raise ApplicationError(
            f"Deposit to {to_account!r} is not allowed (simulated failure)",
            non_retryable=True,
        )

    async with _file_lock:
        accounts = _read_accounts()
        if to_account not in accounts:
            # Auto-create account with zero balance
            accounts[to_account] = 0
        accounts[to_account] = accounts[to_account] + amount
        _write_accounts(accounts)
        activity.logger.info(
            "Deposited %d to %s (new balance: %d)",
            amount,
            to_account,
            accounts[to_account],
        )


@activity.defn
async def refund(from_account: str, amount: int) -> None:
    """Compensation: add *amount* back to *from_account*."""
    async with _file_lock:
        accounts = _read_accounts()
        if from_account not in accounts:
            accounts[from_account] = 0
        accounts[from_account] = accounts[from_account] + amount
        _write_accounts(accounts)
        activity.logger.info(
            "Refunded %d to %s (new balance: %d)",
            amount,
            from_account,
            accounts[from_account],
        )
