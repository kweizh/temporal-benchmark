import { proxyActivities, ActivityFailure, ApplicationFailure } from '@temporalio/workflow';
import type * as activities from './activities';

// Proxy for withdraw and refund: generous retries are fine
const { withdraw, refund } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
  retry: {
    maximumAttempts: 3,
  },
});

// Proxy for deposit: limit attempts so the failure path terminates quickly
const { deposit } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
  retry: {
    maximumAttempts: 1,
  },
});

export interface TransferInput {
  fromAccount: string;
  toAccount: string;
  amount: number;
}

/**
 * MoneyTransfer saga workflow.
 *
 * Happy path  → withdraw → deposit → COMPLETED
 * Failure path → withdraw → deposit (fails) → refund → re-throw → FAILED
 */
export async function MoneyTransfer(input: TransferInput): Promise<void> {
  const { fromAccount, toAccount, amount } = input;

  // Step 1: debit the source account
  await withdraw(fromAccount, amount);

  // Step 2: credit the destination account; compensate on failure
  try {
    await deposit(toAccount, amount);
  } catch (err) {
    // Compensation: refund the source account so its balance is restored
    await refund(fromAccount, amount);

    // Re-surface the original error so the workflow reaches FAILED status.
    // Wrap in ApplicationFailure so Temporal records it cleanly.
    if (err instanceof ActivityFailure && err.cause instanceof ApplicationFailure) {
      throw ApplicationFailure.fromError(err.cause, { message: `Deposit failed; refund issued. Original: ${err.cause.message}` });
    }
    throw err;
  }
}
