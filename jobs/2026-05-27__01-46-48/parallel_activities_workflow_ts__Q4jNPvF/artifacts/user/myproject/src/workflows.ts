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

import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

// Proxy gives us a typed handle to the registered activities.
// startToCloseTimeout is the maximum time a single activity execution may run.
const { squareNumber } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
});

/**
 * ParallelSquaresWorkflow
 *
 * @param numbers - Array of integers to square.
 * @returns       - Sum of the squares of all input numbers.
 */
export async function ParallelSquaresWorkflow(numbers: number[]): Promise<number> {
  // Build all activity promises without awaiting individually so that Temporal
  // schedules them all in parallel (fan-out).
  const squarePromises: Promise<number>[] = numbers.map((n) => squareNumber(n));

  // Fan-in: wait for every activity to complete and collect results.
  const squares: number[] = await Promise.all(squarePromises);

  // Aggregate: sum the squared results.
  const total = squares.reduce((acc, val) => acc + val, 0);

  return total;
}
