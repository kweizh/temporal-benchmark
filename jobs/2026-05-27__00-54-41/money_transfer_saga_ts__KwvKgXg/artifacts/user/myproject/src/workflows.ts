import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { withdraw, deposit, refund } = proxyActivities<typeof activities>({
  startToCloseTimeout: '10 seconds',
  retry: {
    maximumAttempts: 2,
  },
});

export interface TransferInput {
  fromAccount: string;
  toAccount: string;
  amount: number;
}

export async function MoneyTransfer(input: TransferInput): Promise<void> {
  await withdraw(input.fromAccount, input.amount);
  
  try {
    await deposit(input.toAccount, input.amount);
  } catch (err) {
    await refund(input.fromAccount, input.amount);
    throw err;
  }
}
