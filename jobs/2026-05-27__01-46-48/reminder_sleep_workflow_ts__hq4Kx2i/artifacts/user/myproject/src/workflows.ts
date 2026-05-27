import { sleep, proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

// Proxy the Notify activity with a reasonable timeout
const { Notify } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
});

export interface ReminderInput {
  message: string;
  delaySeconds: number;
}

/**
 * ReminderWorkflow: sleeps for delaySeconds, then calls Notify and returns its result.
 */
export async function ReminderWorkflow(input: ReminderInput): Promise<string> {
  const { message, delaySeconds } = input;

  // Deterministic sleep inside the workflow sandbox
  await sleep(delaySeconds * 1000);

  // Invoke the Notify activity and return the result
  return await Notify(message);
}
