import { defineQuery, proxyActivities, setHandler, sleep } from "@temporalio/workflow";
import type * as activities from "./activities";

export interface ProgressInfo {
  progress: number;
  currentStep: number;
  total: number;
}

const { doStep } = proxyActivities<typeof activities>({
  startToCloseTimeout: "30s",
});

export async function ProgressWorkflow(totalSteps: number): Promise<ProgressInfo> {
  let progress = 0;
  let currentStep = 0;

  const getProgress = defineQuery<ProgressInfo>("getProgress");
  setHandler(getProgress, () => ({
    progress,
    currentStep,
    total: totalSteps,
  }));

  for (let step = 1; step <= totalSteps; step += 1) {
    await doStep(step);
    currentStep = step;
    progress = step / totalSteps;
    await sleep("1s");
  }

  return {
    progress,
    currentStep,
    total: totalSteps,
  };
}
