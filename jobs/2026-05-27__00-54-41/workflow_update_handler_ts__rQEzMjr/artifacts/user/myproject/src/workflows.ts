import { defineUpdate, defineSignal, setHandler, condition, ApplicationFailure } from '@temporalio/workflow';

export const depositUpdate = defineUpdate<number, [number]>('deposit');
export const finishSignal = defineSignal('finish');

export async function BankBalanceWorkflow(): Promise<number> {
  let balance = 0;
  let finished = false;

  setHandler(
    depositUpdate,
    (amount: number) => {
      balance += amount;
      return balance;
    },
    {
      validator: (amount: number) => {
        if (amount <= 0) {
          throw ApplicationFailure.create({ message: 'Amount must be positive', type: 'InvalidAmount' });
        }
      }
    }
  );

  setHandler(finishSignal, () => {
    finished = true;
  });

  await condition(() => finished);

  return balance;
}
