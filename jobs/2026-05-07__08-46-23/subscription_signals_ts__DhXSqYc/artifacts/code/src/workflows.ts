import {
  defineSignal,
  setHandler,
  sleep,
  proxyActivities,
  condition,
} from '@temporalio/workflow';
import type * as activities from './activities';

const { chargeUser } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export const updateTierSignal = defineSignal<[string]>('updateTierSignal');
export const cancelSubscriptionSignal = defineSignal('cancelSubscriptionSignal');

interface SubscriptionArgs {
  initialTier: string;
  billingPeriodMs: number;
}

export async function subscriptionWorkflow(args: SubscriptionArgs): Promise<string> {
  let currentTier = args.initialTier;
  let isCanceled = false;

  setHandler(updateTierSignal, (newTier: string) => {
    currentTier = newTier;
  });

  setHandler(cancelSubscriptionSignal, () => {
    isCanceled = true;
  });

  while (!isCanceled) {
    // Wait for the billing period or until canceled
    const canceled = await condition(() => isCanceled, args.billingPeriodMs);
    
    if (canceled) {
      break;
    }

    await chargeUser(currentTier);
  }

  return 'Canceled';
}
