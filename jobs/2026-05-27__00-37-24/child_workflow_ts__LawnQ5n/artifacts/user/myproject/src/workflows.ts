import { executeChild } from '@temporalio/workflow';

export async function DoubleWorkflow(n: number): Promise<number> {
  return n * 2;
}

export async function ParentSumWorkflow(numbers: number[]): Promise<number> {
  const results = await Promise.all(
    numbers.map((n) =>
      executeChild(DoubleWorkflow, {
        args: [n],
      })
    )
  );
  return results.reduce((sum, val) => sum + val, 0);
}
