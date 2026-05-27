// DiscountWorkflow picks a percentage discount for a user.
//
// NOTE: This implementation is intentionally broken. It violates Temporal's
// deterministic execution constraints by reading the wall-clock time and
// generating random numbers directly inside the Workflow body.
//
// Your task is to refactor this Workflow so that:
//   * The current time is obtained through a Temporal Workflow-safe API
//     (e.g. `workflow.now()`), not via `new Date(...)`.
//   * Random discount selection is delegated to an Activity named
//     `pickDiscount` declared in `./activities`, which the Workflow invokes
//     through `proxyActivities`.

import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { pickDiscount } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export interface DiscountResult {
  userId: string;
  discount: number;
  decidedAt: number;
}

export async function DiscountWorkflow(userId: string): Promise<DiscountResult> {
  const discount = await pickDiscount();
  const decidedAt = Date.now();
  return { userId, discount, decidedAt };
}
