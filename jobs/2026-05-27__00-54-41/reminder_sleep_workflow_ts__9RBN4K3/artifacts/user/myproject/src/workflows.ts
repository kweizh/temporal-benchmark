import { proxyActivities, sleep } from '@temporalio/workflow';
import type * as activities from './activities';

const { Notify } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export async function ReminderWorkflow(input: { message: string; delaySeconds: number }): Promise<string> {
  await sleep(input.delaySeconds * 1000);
  return await Notify(input.message);
}
