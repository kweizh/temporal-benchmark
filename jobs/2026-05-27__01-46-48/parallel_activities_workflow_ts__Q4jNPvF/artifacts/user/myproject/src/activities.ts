/**
 * Temporal Activities
 *
 * squareNumber: accepts an integer n and returns n * n.
 * This is a deterministic compute step executed by the Temporal worker.
 */

export async function squareNumber(n: number): Promise<number> {
  return n * n;
}
