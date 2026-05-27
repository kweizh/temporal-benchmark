import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { withdraw, deposit, refund } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
  retry: {
    maximumAttempts: 2,
  },
});

interface MoneyTransferInput {
  fromAccount: string;
  toAccount: string;
  amount: number;
}

export async function MoneyTransfer(input: MoneyTransferInput): Promise<void> {
  const { fromAccount, toAccount, amount } = input;

  await withdraw(fromAccount, amount);

  try {
    await deposit(toAccount, amount);
  } catch (err) {
    console.log(`Deposit failed, initiating refund to ${fromAccount}`);
    await refund(fromAccount, amount);
    throw err;
  }
}
