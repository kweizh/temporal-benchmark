import {
  proxyActivities,
  CancellationScope,
  isCancellation,
  ActivityCancellationType,
} from '@temporalio/workflow';
import type * as activities from './activities';

const { doWork, cleanup } = proxyActivities<typeof activities>({
  startToCloseTimeout: '2m',
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
      console.log('Workflow caught cancellation, running cleanup');
      await CancellationScope.nonCancellable(async () => {
        const result = await cleanup();
        console.log(`Cleanup result: ${result}`);
      });
      throw err; // Rethrow to mark workflow as CANCELED
    }
    throw err;
  }
}
