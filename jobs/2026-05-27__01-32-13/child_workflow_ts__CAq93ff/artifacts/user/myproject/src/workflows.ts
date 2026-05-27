import { executeChild } from '@temporalio/workflow';

export async function DoubleWorkflow(n: number): Promise<number> {
  return n * 2;
}

export async function ParentSumWorkflow(numbers: number[]): Promise<number> {
  const doubledValues = await Promise.all(
    numbers.map((value) => executeChild(DoubleWorkflow, { args: [value] }))
  );

  return doubledValues.reduce((sum, value) => sum + value, 0);
}
