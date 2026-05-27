import { startWorker } from './worker.js';
import { runClient } from './client.js';

async function main() {
  const worker = await startWorker();
  const runPromise = worker.run();

  try {
    await runClient();
  } finally {
    worker.shutdown();
    await runPromise;
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
