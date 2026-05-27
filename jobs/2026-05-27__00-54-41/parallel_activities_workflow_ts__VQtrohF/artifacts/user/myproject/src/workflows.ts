import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { squareNumber } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export async function ParallelSquaresWorkflow(numbers: number[]): Promise<number> {
  const promises = numbers.map((n) => squareNumber(n));
  const results = await Promise.all(promises);
  return results.reduce((sum, current) => sum + current, 0);
}