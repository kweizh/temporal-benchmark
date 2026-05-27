import { heartbeat, sleep, CancelledFailure } from '@temporalio/activity';

/**
 * Long-running activity that simulates work for ~60 seconds.
 * Heartbeats every ~500ms so cancellation is delivered promptly.
 * When cancelled, the sleep() call will throw CancelledFailure which we rethrow.
 */
export async function doWork(): Promise<void> {
  console.log('[doWork] Starting work loop (~60 seconds)...');
  // Loop for up to 120 iterations × 500ms = ~60 seconds
  for (let i = 0; i < 120; i++) {
    heartbeat({ iteration: i, message: 'working' });
    try {
      await sleep(500);
    } catch (err) {
      if (err instanceof CancelledFailure) {
        console.log(`[doWork] Cancellation received at iteration ${i}, rethrowing.`);
        throw err;
      }
      throw err;
    }
    if (i % 10 === 0) {
      console.log(`[doWork] Iteration ${i}/120`);
    }
  }
  console.log('[doWork] Work loop completed normally.');
}

/**
 * Compensation activity that runs even when the workflow is being cancelled.
 * Returns the literal string "cleanup-done".
 */
export async function cleanup(): Promise<string> {
  console.log('[cleanup] Running cleanup compensation...');
  const result = 'cleanup-done';
  console.log(`[cleanup] Cleanup complete, returning: ${result}`);
  return result;
}
