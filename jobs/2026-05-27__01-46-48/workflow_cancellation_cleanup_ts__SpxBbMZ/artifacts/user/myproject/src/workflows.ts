import {
  proxyActivities,
  CancellationScope,
  isCancellation,
  ActivityCancellationType,
  log,
} from '@temporalio/workflow';

// Import type only — workflow sandbox cannot import activity implementation
import type * as activities from './activities';

/**
 * Proxy for doWork:
 *  - startToCloseTimeout longer than the ~60s work loop
 *  - heartbeatTimeout short so cancellation is detected quickly
 *  - TRY_CANCEL so the workflow doesn't have to wait for doWork to
 *    acknowledge cancellation before proceeding to the cleanup branch
 */
const { doWork } = proxyActivities<typeof activities>({
  startToCloseTimeout: '120 seconds',
  heartbeatTimeout: '10 seconds',
  cancellationType: ActivityCancellationType.TRY_CANCEL,
});

/**
 * Proxy for cleanup:
 *  - Runs inside a nonCancellable scope so it cannot be cancelled itself.
 *  - No cancellationType override needed.
 */
const { cleanup } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
});

/**
 * CancellableWorkflow
 *
 * Pattern:
 *  1. Run doWork inside a cancellable scope.
 *  2. If the workflow is cancelled, isCancellation(err) will be true.
 *  3. Run cleanup inside a nonCancellable scope so it survives the
 *     surrounding cancellation.
 *  4. Rethrow the original CancelledFailure so Temporal records the
 *     execution with status CANCELED.
 */
export async function CancellableWorkflow(): Promise<void> {
  log.info('CancellableWorkflow started');

  try {
    await CancellationScope.cancellable(async () => {
      await doWork();
    });
  } catch (err) {
    if (isCancellation(err)) {
      log.info('Cancellation detected — running cleanup in nonCancellable scope');

      // Shield cleanup from the parent scope's cancellation so it always runs
      await CancellationScope.nonCancellable(async () => {
        await cleanup();
      });

      log.info('Cleanup completed — rethrowing cancellation');
      // Rethrow so the workflow execution is recorded as CANCELED
      throw err;
    }
    // Unexpected error — propagate as-is
    throw err;
  }

  log.info('CancellableWorkflow completed normally (no cancellation)');
}
