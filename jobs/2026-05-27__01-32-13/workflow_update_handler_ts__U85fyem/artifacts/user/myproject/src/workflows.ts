import { ApplicationFailure } from '@temporalio/common';
import { condition, defineSignal, defineUpdate, setHandler } from '@temporalio/workflow';

export const deposit = defineUpdate<number, [number]>('deposit');
export const finish = defineSignal('finish');

export async function BankBalanceWorkflow(): Promise<number> {
  let balance = 0;
  let finished = false;

  setHandler(
    deposit,
    (amount: number) => {
      balance += amount;
      return balance;
    },
    {
      validator: (amount: number) => {
        if (amount <= 0) {
          throw ApplicationFailure.create({
            message: 'Amount must be a positive number',
            type: 'InvalidAmount',
          });
        }
      },
    }
  );

  setHandler(finish, () => {
    finished = true;
  });

  await condition(() => finished);
  return balance;
}
