import * as workflow from '@temporalio/workflow';
import type { doStep as doStepActivity } from './activities';

const { sleep, proxyActivities, defineQuery, setHandler } = workflow;

const activities = proxyActivities<{ doStep: typeof doStepActivity }>({
  startToCloseTimeout: '30s',
});

export const getProgressQuery = defineQuery<{ progress: number; currentStep: number; total: number }>('getProgress');

export async function ProgressWorkflow(totalSteps: number): Promise<{ progress: number; currentStep: number; total: number }> {
  let progress = 0;
  let currentStep = 0;

  setHandler(getProgressQuery, () => ({
    progress,
    currentStep,
    total: totalSteps,
  }));

  for (let i = 1; i <= totalSteps; i++) {
    await activities.doStep(i);
    currentStep = i;
    progress = i / totalSteps;
    if (i < totalSteps) {
      await sleep('1s');
    }
  }

  return { progress, currentStep, total: totalSteps };
}
