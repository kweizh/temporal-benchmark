import {
  defineSignal,
  defineQuery,
  proxyActivities,
  setHandler,
  sleep,
} from '@temporalio/workflow';

export interface SubscriptionInput {
  userId: string;
  tier: string;
}

export interface SubscriptionStatus {
  tier: string;
  billings: number;
  cancelled: boolean;
}

export interface SubscriptionResult {
  billings: number;
  finalTier: string;
  cancelled: boolean;
}

const upgradeSignal = defineSignal<[string]>('upgrade');
const cancelSignal = defineSignal('cancel');
const getStatusQuery = defineQuery<SubscriptionStatus>('getStatus');

const { chargeCard } = proxyActivities<{
  chargeCard: (userId: string, tier: string) => Promise<void>;
}>({
  startToCloseTimeout: '1 minute',
});

export async function SubscriptionWorkflow(
  input: SubscriptionInput
): Promise<SubscriptionResult> {
  let tier = input.tier;
  let billings = 0;
  let cancelled = false;

  setHandler(upgradeSignal, (newTier) => {
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

  for (let period = 0; period < 12; period += 1) {
    if (cancelled) {
      break;
    }

    await chargeCard(input.userId, tier);
    billings += 1;

    if (cancelled) {
      break;
    }

    await sleep(2000);
  }

  return {
    billings,
    finalTier: tier,
    cancelled,
  };
}

export const signals = {
  upgradeSignal,
  cancelSignal,
};

export const queries = {
  getStatusQuery,
};
