import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { fetchData } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
});

export async function FetchUrlWorkflow(url: string): Promise<string> {
  return await fetchData(url);
}
