import { continueAsNew, proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { incrementCounter } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

/**
 * BROKEN: This implementation loops from `start` to `target` in a single
 * Run Id. For long loops this accumulates a huge event history and risks
 * hitting Temporal's history limits. Refactor it to call `continueAsNew`
 * every 10 iterations, passing the current counter value forward as the
 * new `start` argument.
 */
export async function LongLoopWorkflow(start: number, target: number): Promise<number> {
  let counter = start;
  let iterations = 0;

  while (counter < target) {
    counter = await incrementCounter(counter);
    iterations += 1;

    if (iterations % 10 === 0 && counter < target) {
      await continueAsNew<typeof LongLoopWorkflow>(counter, target);
    }
  }

  return counter;
}
