import { runWorker } from './worker';
import { runClient } from './client';

async function main(): Promise<void> {
  const worker = await runWorker();
  const workerRun = worker.run();
  try {
    await runClient();
  } finally {
    worker.shutdown();
    await workerRun;
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
