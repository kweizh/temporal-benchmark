/**
 * Temporal Workflow: ParallelSquaresWorkflow
 *
 * Accepts an array of numbers, fans out by invoking the squareNumber activity
 * concurrently for every element via Promise.all (fan-out), then sums the
 * squared results (fan-in) and returns the total.
 *
 * NOTE: This file runs inside the Temporal workflow sandbox.
 * Only @temporalio/workflow imports are allowed here — no Node.js built-ins.
 */
/**
 * ParallelSquaresWorkflow
 *
 * @param numbers - Array of integers to square.
 * @returns       - Sum of the squares of all input numbers.
 */
export declare function ParallelSquaresWorkflow(numbers: number[]): Promise<number>;
//# sourceMappingURL=workflows.d.ts.map