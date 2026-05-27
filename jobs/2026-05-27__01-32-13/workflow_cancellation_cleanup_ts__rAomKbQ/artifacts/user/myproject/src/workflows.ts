import {
  ActivityCancellationType,
  CancellationScope,
  isCancellation,
  proxyActivities,
} from '@temporalio/workflow';
import type * as activities from './activities';

const { doWork, cleanup } = proxyActivities<typeof activities>({
  startToCloseTimeout: '90s',
  heartbeatTimeout: '10s',
  cancellationType: ActivityCancellationType.TRY_CANCEL,
});

export async function CancellableWorkflow(): Promise<void> {
  try {
    await CancellationScope.cancellable(async () => {
      await doWork();
    });
  } catch (err) {
    if (isCancellation(err)) {
      await CancellationScope.nonCancellable(async () => cleanup());
      throw err;
    }
    throw err;
  }
}
