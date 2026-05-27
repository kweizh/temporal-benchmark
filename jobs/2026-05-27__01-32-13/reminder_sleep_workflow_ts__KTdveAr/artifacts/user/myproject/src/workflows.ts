import { proxyActivities, sleep } from '@temporalio/workflow';

export interface ReminderInput {
  message: string;
  delaySeconds: number;
}

const { Notify } = proxyActivities<{ Notify(message: string): Promise<string> }>({
  startToCloseTimeout: '1 minute',
});

export async function ReminderWorkflow(input: ReminderInput): Promise<string> {
  await sleep(input.delaySeconds * 1000);
  return Notify(input.message);
}
