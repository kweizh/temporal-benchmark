import {
  defineUpdate,
  defineSignal,
  setHandler,
  condition,
} from '@temporalio/workflow';
import { ApplicationFailure } from '@temporalio/common';

export const depositUpdate = defineUpdate<number, [number]>('deposit');
export const finishSignal = defineSignal('finish');

export async function BankBalanceWorkflow(): Promise<number> {
  let balance = 0;
  let isFinished = false;

  setHandler(
    depositUpdate,
    (amount: number) => {
      balance += amount;
      return balance;
    },
    {
      validator: (amount: number) => {
        if (amount <= 0) {
          throw ApplicationFailure.create({
            message: 'Amount must be positive',
            type: 'InvalidAmount',
          });
        }
      },
    }
  );

  setHandler(finishSignal, () => {
    isFinished = true;
  });

  await condition(() => isFinished);

  return balance;
}
