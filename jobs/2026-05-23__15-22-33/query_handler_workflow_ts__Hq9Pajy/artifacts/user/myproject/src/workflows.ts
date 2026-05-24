import { proxyActivities, defineQuery, setHandler, sleep } from '@temporalio/workflow';
import type * as activities from './activities.js';

const { doStep } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30s',
});

export const getProgressQuery = defineQuery<{ progress: number; currentStep: number; total: number }>('getProgress');

export async function ProgressWorkflow(totalSteps: number): Promise<{ progress: number; currentStep: number; total: number }> {
  let currentStep = 0;
  let progress = 0;

  setHandler(getProgressQuery, () => ({
    progress,
    currentStep,
    total: totalSteps,
  }));

  for (let i = 1; i <= totalSteps; i++) {
    await doStep(i);
    currentStep = i;
    progress = i / totalSteps;
    await sleep('1s');
  }

  return {
    progress,
    currentStep,
    total: totalSteps,
  };
}
