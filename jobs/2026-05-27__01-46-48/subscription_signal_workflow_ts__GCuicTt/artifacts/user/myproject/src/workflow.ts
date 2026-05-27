import {
  defineSignal,
  defineQuery,
  setHandler,
  condition,
  sleep,
  proxyActivities,
} from '@temporalio/workflow';
import type { Activities } from './activities';

// Define signals
export const upgradeSignal = defineSignal<[string]>('upgrade');
export const cancelSignal = defineSignal('cancel');

// Define query
export const getStatusQuery = defineQuery<{
  tier: string;
  billings: number;
  cancelled: boolean;
}>('getStatus');

// Proxy activities with a reasonable timeout
const { chargeCard } = proxyActivities<Activities>({
  startToCloseTimeout: '30 seconds',
});

export interface SubscriptionInput {
  userId: string;
  tier: string;
}

export interface SubscriptionResult {
  billings: number;
  finalTier: string;
  cancelled: boolean;
}

export async function SubscriptionWorkflow(
  input: SubscriptionInput
): Promise<SubscriptionResult> {
  const { userId } = input;

  // Mutable state
  let tier = input.tier;
  let billings = 0;
  let cancelled = false;

  // Register signal handlers
  setHandler(upgradeSignal, (newTier: string) => {
    tier = newTier;
  });

  setHandler(cancelSignal, () => {
    cancelled = true;
  });

  // Register query handler
  setHandler(getStatusQuery, () => ({
    tier,
    billings,
    cancelled,
  }));

  // Run up to 12 billing periods
  for (let period = 0; period < 12; period++) {
    // Check for cancellation before starting a new period
    if (cancelled) {
      break;
    }

    // Wait between periods (skip sleep before the very first period)
    if (period > 0) {
      // Sleep for 2000ms but also wake up early if cancelled
      await Promise.race([
        sleep(2000),
        condition(() => cancelled),
      ]);

      // If cancelled during sleep, exit without charging
      if (cancelled) {
        break;
      }
    }

    // Charge card for current period using the current tier
    await chargeCard(userId, tier);
    billings++;
  }

  return {
    billings,
    finalTier: tier,
    cancelled,
  };
}
