import { proxyActivities } from "@temporalio/workflow";
import type * as activities from "./activities";

const { squareNumber } = proxyActivities<typeof activities>({
  startToCloseTimeout: "1 minute",
});

export async function ParallelSquaresWorkflow(numbers: number[]): Promise<number> {
  const activityPromises = numbers.map((value) => squareNumber(value));
  const results = await Promise.all(activityPromises);
  return results.reduce((sum, value) => sum + value, 0);
}
