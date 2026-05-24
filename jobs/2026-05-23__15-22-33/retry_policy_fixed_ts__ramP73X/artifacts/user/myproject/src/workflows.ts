import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { flakyTask } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
  retry: {
    maximumAttempts: 5,
    initialInterval: '2 seconds',
    backoffCoefficient: 1.0,
  },
});

export async function FlakyWorkflow(): Promise<string> {
  try {
    await flakyTask();
    return 'success'; // Should not reach here
  } catch (err) {
    return 'failed after 5 attempts';
  }
}
