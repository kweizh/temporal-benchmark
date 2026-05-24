import { proxyActivities, sleep, patched } from '@temporalio/workflow';
import type * as activities from './activities';

const { chargeCard, shipOrder, notifyCustomer } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
});

export async function OrderWorkflow(orderId: string): Promise<void> {
  await chargeCard(orderId);
  if (patched('add-notify-customer')) {
    await notifyCustomer(orderId);
  }
  await sleep('10 seconds');
  await shipOrder(orderId);
}
