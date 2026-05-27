import { ApplicationFailure } from '@temporalio/activity';
import * as fs from 'fs';

const ACCOUNTS_FILE = '/workspace/accounts.json';

/**
 * Read the accounts JSON, apply a mutation, then write it back atomically.
 */
function mutateAccounts(fn: (accounts: Record<string, number>) => void): void {
  // Read
  const raw = fs.readFileSync(ACCOUNTS_FILE, 'utf8');
  const accounts: Record<string, number> = JSON.parse(raw);

  // Mutate
  fn(accounts);

  // Write (overwrite in place; this is single-process so no locking needed)
  fs.writeFileSync(ACCOUNTS_FILE, JSON.stringify(accounts, null, 2), 'utf8');
}

/**
 * Subtract `amount` from `accounts[account]`.
 */
export async function withdraw(account: string, amount: number): Promise<void> {
  console.log(`[activity] withdraw: account=${account} amount=${amount}`);
  mutateAccounts((accounts) => {
    const current = accounts[account] ?? 0;
    accounts[account] = current - amount;
  });
  console.log(`[activity] withdraw complete`);
}

/**
 * Add `amount` to `accounts[account]`.
 * If `account === "B_FAIL"`, throw a non-retryable error to simulate failure.
 */
export async function deposit(account: string, amount: number): Promise<void> {
  console.log(`[activity] deposit: account=${account} amount=${amount}`);

  if (account === 'B_FAIL') {
    // Non-retryable: mark as non-retryable so Temporal honours maximumAttempts=1
    throw ApplicationFailure.nonRetryable(
      `Deposit to account "${account}" is not allowed (simulated failure)`,
      'DepositFailed',
    );
  }

  mutateAccounts((accounts) => {
    const current = accounts[account] ?? 0;
    accounts[account] = current + amount;
  });
  console.log(`[activity] deposit complete`);
}

/**
 * Add `amount` back to `accounts[account]` — reverses a prior withdraw.
 */
export async function refund(account: string, amount: number): Promise<void> {
  console.log(`[activity] refund: account=${account} amount=${amount}`);
  mutateAccounts((accounts) => {
    const current = accounts[account] ?? 0;
    accounts[account] = current + amount;
  });
  console.log(`[activity] refund complete`);
}
