import { startWorker } from './worker';
import { runClient } from './client';

async function main() {
  const worker = await startWorker();
  
  // Start worker in the background
  const workerPromise = worker.run();

  try {
    await runClient();
  } catch (err) {
    console.error('Client error:', err);
    process.exit(1);
  }

  // Once the client is done, we can exit the process
  process.exit(0);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
