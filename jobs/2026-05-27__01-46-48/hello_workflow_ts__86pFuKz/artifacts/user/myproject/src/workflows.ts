import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { greet } = proxyActivities<typeof activities>({
  startToCloseTimeout: '10 seconds',
});

export async function HelloWorkflow(name: string): Promise<string> {
  return await greet(name);
}
