import { proxyActivities, continueAsNew } from '@temporalio/workflow';
import type * as activities from './activities';

const { incrementCounter } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

/**
 * Refactored to call `continueAsNew` every 10 iterations.
 */
export async function LongLoopWorkflow(start: number, target: number): Promise<number> {
  let counter = start;
  let iterations = 0;

  while (counter < target) {
    counter = await incrementCounter(counter);
    iterations++;

    if (iterations >= 10 && counter < target) {
      await continueAsNew<typeof LongLoopWorkflow>(counter, target);
    }
  }

  return counter;
}
