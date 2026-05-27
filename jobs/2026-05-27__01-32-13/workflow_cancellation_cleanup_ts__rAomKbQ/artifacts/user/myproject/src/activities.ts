import { heartbeat, isCancellation } from '@temporalio/activity';

const WORK_DURATION_MS = 60_000;
const HEARTBEAT_INTERVAL_MS = 500;

export async function doWork(): Promise<void> {
  const start = Date.now();

  while (Date.now() - start < WORK_DURATION_MS) {
    try {
      heartbeat({ progressMs: Date.now() - start });
    } catch (err) {
      if (isCancellation(err)) {
        throw err;
      }
      throw err;
    }

    await new Promise((resolve) => setTimeout(resolve, HEARTBEAT_INTERVAL_MS));
  }
}

export async function cleanup(): Promise<string> {
  return 'cleanup-done';
}
