import { proxyActivities, defineQuery, setHandler, sleep } from '@temporalio/workflow';
import type * as activities from './activities';

const { doStep } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
});

export const getProgress = defineQuery<{ progress: number; currentStep: number; total: number }>('getProgress');

export async function ProgressWorkflow(totalSteps: number): Promise<{ progress: number; currentStep: number; total: number }> {
  let progress = 0;
  let currentStep = 0;

  setHandler(getProgress, () => ({
    progress,
    currentStep,
    total: totalSteps,
  }));

  for (let i = 1; i <= totalSteps; i++) {
    await doStep(i);
    currentStep = i;
    progress = i / totalSteps;
    if (i < totalSteps) {
      await sleep('1s');
    }
  }

  return { progress, currentStep, total: totalSteps };
}