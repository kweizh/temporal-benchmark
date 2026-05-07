import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { withdraw, deposit, refund } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export async function moneyTransferSaga(
  fromAccountId: string,
  toAccountId: string,
  amount: number
): Promise<void> {
  await withdraw(fromAccountId, amount);

  try {
    await deposit(toAccountId, amount);
  } catch (error) {
    console.error('Deposit failed, starting compensation...');
    await refund(fromAccountId, amount);
    throw error;
  }
}
