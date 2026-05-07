import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { fetchData } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export async function exampleWorkflow(): Promise<any> {
  return await fetchData();
}
