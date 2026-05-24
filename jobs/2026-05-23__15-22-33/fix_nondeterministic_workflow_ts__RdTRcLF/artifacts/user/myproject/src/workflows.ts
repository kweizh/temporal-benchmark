import { proxyActivities, workflow } from '@temporalio/workflow';
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
  const decidedAt = workflow.now();
  return { userId, discount, decidedAt };
}
