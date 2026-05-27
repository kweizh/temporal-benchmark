import { executeChild } from '@temporalio/workflow';

/**
 * DoubleWorkflow accepts a single number `n` and returns `n * 2`.
 */
export async function DoubleWorkflow(n: number): Promise<number> {
  return n * 2;
}

/**
 * ParentSumWorkflow accepts an array of numbers, invokes DoubleWorkflow
 * once per element via executeChild, and returns the sum of all doubled values.
 */
export async function ParentSumWorkflow(numbers: number[]): Promise<number> {
  const doubled = await Promise.all(
    numbers.map((n, index) =>
      executeChild(DoubleWorkflow, {
        args: [n],
        taskQueue: 'child-workflow-ts',
        workflowId: `child-double-${index}-${n}`,
      })
    )
  );

  return doubled.reduce((sum, val) => sum + val, 0);
}
