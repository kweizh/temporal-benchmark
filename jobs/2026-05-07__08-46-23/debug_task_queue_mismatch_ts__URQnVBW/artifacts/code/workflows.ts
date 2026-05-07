import { proxyActivities } from '@temporalio/workflow';

export async function MyWorkflow(): Promise<string> {
  return 'Hello, Temporal!';
}
