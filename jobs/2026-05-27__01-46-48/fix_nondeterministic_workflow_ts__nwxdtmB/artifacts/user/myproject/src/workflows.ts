// DiscountWorkflow picks a percentage discount for a user.
//
// Time is obtained via `Date.now()` which the Temporal SDK overrides inside
// Workflow code to return a deterministic, replay-safe timestamp (frozen at
// the start of each Workflow Task).
//
// Random discount selection is delegated to the `pickDiscount` Activity so
// that the Workflow body remains fully deterministic and replay-safe.

import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { pickDiscount } = proxyActivities<typeof activities>({
  startToCloseTimeout: '10 seconds',
});

export interface DiscountResult {
  userId: string;
  discount: number;
  decidedAt: number;
}

export async function DiscountWorkflow(userId: string): Promise<DiscountResult> {
  // Delegate randomness to an Activity – safe for replay.
  const discount = await pickDiscount();
  // Date.now() is patched by the Temporal SDK to be deterministic inside
  // Workflow code (frozen at the start of each Workflow Task).
  const decidedAt = Date.now();
  return { userId, discount, decidedAt };
}
