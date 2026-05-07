import { patched, proxyActivities, sleep } from '@temporalio/workflow';
import type * as activities from './activities';

const { chargeCustomer, chargeCustomerV2 } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export async function processOrder(orderId: string): Promise<string> {
  await sleep('100 milliseconds');
  if (patched('use-v2-charge')) {
    await chargeCustomerV2(orderId);
  } else {
    await chargeCustomer(orderId);
  }
  return 'processed';
}
