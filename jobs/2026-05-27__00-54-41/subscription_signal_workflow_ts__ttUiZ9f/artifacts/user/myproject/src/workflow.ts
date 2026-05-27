import {
  proxyActivities,
  defineSignal,
  defineQuery,
  setHandler,
  condition,
  sleep,
} from '@temporalio/workflow';
import type * as activities from './activities';

const { chargeCard } = proxyActivities<typeof activities>({
  startToCloseTimeout: '10 seconds',
});

export const upgradeSignal = defineSignal<[string]>('upgrade');
export const cancelSignal = defineSignal<[]>('cancel');
export const getStatusQuery = defineQuery<
  { tier: string; billings: number; cancelled: boolean }
>('getStatus');

export interface SubscriptionInput {
  userId: string;
  tier: string;
}

export interface SubscriptionOutput {
  billings: number;
  finalTier: string;
  cancelled: boolean;
}

export async function SubscriptionWorkflow(
  input: SubscriptionInput
): Promise<SubscriptionOutput> {
  let currentTier = input.tier;
  let billings = 0;
  let cancelled = false;

  setHandler(upgradeSignal, (newTier: string) => {
    currentTier = newTier;
  });

  setHandler(cancelSignal, () => {
    cancelled = true;
  });

  setHandler(getStatusQuery, () => {
    return {
      tier: currentTier,
      billings,
      cancelled,
    };
  });

  for (let i = 0; i < 12; i++) {
    if (cancelled) {
      break;
    }

    await chargeCard(input.userId, currentTier);
    billings++;

    // Wait for 2000ms or until cancelled
    // The instructions mention both workflow.sleep(2000) and workflow.condition(...)
    // Using condition allows us to wake up early on cancel.
    await condition(() => cancelled, 2000);
  }

  return {
    billings,
    finalTier: currentTier,
    cancelled,
  };
}
