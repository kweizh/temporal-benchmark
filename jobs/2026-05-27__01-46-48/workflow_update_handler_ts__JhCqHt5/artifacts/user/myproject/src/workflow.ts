import {
  defineUpdate,
  defineSignal,
  setHandler,
  condition,
} from '@temporalio/workflow';
import { ApplicationFailure } from '@temporalio/common';

// Define the deposit Update: takes a number (amount), returns a number (new balance)
export const depositUpdate = defineUpdate<number, [number]>('deposit');

// Define the finish Signal: no arguments
export const finishSignal = defineSignal('finish');

export async function BankBalanceWorkflow(): Promise<number> {
  let balance = 0;
  let finished = false;

  // Register the finish signal handler
  setHandler(finishSignal, () => {
    finished = true;
  });

  // Register the deposit update handler with a validator
  setHandler(
    depositUpdate,
    (amount: number): number => {
      balance += amount;
      return balance;
    },
    {
      validator: (amount: number): void => {
        if (amount <= 0) {
          throw ApplicationFailure.create({
            message: `Deposit amount must be positive, got: ${amount}`,
            type: 'InvalidAmount',
          });
        }
      },
    }
  );

  // Wait until the finish signal is received (no busy-loop)
  await condition(() => finished);

  return balance;
}
