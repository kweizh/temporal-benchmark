import { proxyActivities, continueAsNew } from '@temporalio/workflow';
import type * as activities from './activities';

const { incrementCounter } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

/**
 * LongLoopWorkflow loops from `start` up to `target`, calling
 * `incrementCounter` on each iteration. Every 10 iterations within
 * a single Run Id it calls `continueAsNew`, passing the current counter
 * forward as the new `start` so the chain continues with a fresh history.
 */
export async function LongLoopWorkflow(start: number, target: number): Promise<number> {
  let counter = start;
  let iterationsThisRun = 0;

  while (counter < target) {
    counter = await incrementCounter(counter);
    iterationsThisRun++;

    if (iterationsThisRun === 10 && counter < target) {
      await continueAsNew<typeof LongLoopWorkflow>(counter, target);
    }
  }

  return counter;
}
