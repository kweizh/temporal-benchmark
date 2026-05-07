import { proxyActivities, sleep } from '@temporalio/workflow';
import type * as activities from './activities';

const { notify } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export async function reminderWorkflow(durationMs: number, message: string): Promise<string> {
  await sleep(durationMs);
  return await notify(message);
}
