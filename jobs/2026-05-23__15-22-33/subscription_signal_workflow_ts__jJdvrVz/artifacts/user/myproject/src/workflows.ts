import {
  proxyActivities,
  defineSignal,
  defineQuery,
  setHandler,
  sleep,
  condition,
} from '@temporalio/workflow';
import type * as activities from './activities';

const { chargeCard } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export const upgradeSignal = defineSignal<[string]>('upgrade');
export const cancelSignal = defineSignal('cancel');
export const getStatusQuery = defineQuery<{
  tier: string;
  billings: number;
  cancelled: boolean;
}>('getStatus');

export async function SubscriptionWorkflow(input: {
  userId: string;
  tier: string;
}): Promise<{
  billings: number;
  finalTier: string;
  cancelled: boolean;
}> {
  let tier = input.tier;
  let billings = 0;
  let cancelled = false;

  setHandler(upgradeSignal, (newTier: string) => {
    tier = newTier;
  });

  setHandler(cancelSignal, () => {
    cancelled = true;
  });

  setHandler(getStatusQuery, () => ({
    tier,
    billings,
    cancelled,
  }));

  for (let i = 0; i < 12; i++) {
    if (cancelled) break;

    await chargeCard(input.userId, tier);
    billings++;

    // Wait for 2 seconds or until cancelled
    // Requirements say: "Between periods it must wait by calling the workflow sleep API with 2000 ms"
    // However, it also says "The cancel signal should make the workflow break out of its billing loop without throwing"
    // and "it must accept external requests during the run: a user may upgrade their tier or cancel their subscription at any moment."
    // If I just sleep(2000), it won't react to cancel until the sleep is over.
    // Use condition to wait up to 2000ms but wake up if cancelled.
    // Wait, requirement says: "it must wait by calling the workflow sleep API with 2000 ms"
    // Let's stick to sleep(2000) as requested, but check cancelled after sleep.
    // Actually, "at any moment" suggests responsiveness.
    // But "calling the workflow sleep API with 2000 ms" is specific.
    
    await sleep(2000);
  }

  // "In each period (and before exiting), it must invoke an Activity chargeCard(userId, tier) with the current tier"
  // This implies one more chargeCard before exiting if it wasn't already charged for the final state?
  // Let's re-read: "In each period (and before exiting), it must invoke an Activity chargeCard"
  // If cancelled, should it charge one last time? 
  // "After receiving cancel, the workflow must not start any new billing period."
  // Usually "before exiting" means a final charge.
  
  if (!cancelled) {
      // The loop ran 12 times. Does "before exiting" mean a 13th charge?
      // "Iterates through up to 12 billing periods."
      // Let's assume the charge inside the loop is the "period" charge.
      // If the loop finishes naturally, it has charged 12 times.
  }

  return {
    billings,
    finalTier: tier,
    cancelled,
  };
}
