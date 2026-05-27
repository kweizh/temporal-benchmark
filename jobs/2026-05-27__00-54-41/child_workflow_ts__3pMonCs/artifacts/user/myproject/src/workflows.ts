import { executeChild } from '@temporalio/workflow';

export async function DoubleWorkflow(n: number): Promise<number> {
  return n * 2;
}

export async function ParentSumWorkflow(numbers: number[]): Promise<number> {
  let sum = 0;
  for (const n of numbers) {
    const doubled = await executeChild(DoubleWorkflow, {
      args: [n],
    });
    sum += doubled;
  }
  return sum;
}
