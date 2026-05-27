import { createWorker } from './worker';
import { runClient } from './client';

async function main(): Promise<void> {
  const worker = await createWorker();
  const workerRun = worker.run();

  await new Promise((resolve) => setTimeout(resolve, 1500));

  try {
    await runClient();
  } finally {
    await worker.shutdown();
    await workerRun;
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
