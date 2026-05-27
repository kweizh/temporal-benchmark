import { spawn } from 'node:child_process';
import { runClient } from './client';

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function run(): Promise<void> {
  const workerProcess = spawn('ts-node', ['src/worker.ts'], {
    stdio: 'inherit',
  });

  workerProcess.on('exit', (code) => {
    if (code !== null && code !== 0) {
      console.error(`Worker exited with code ${code}`);
    }
  });

  await wait(1500);

  try {
    const result = await runClient();
    console.log(result);
  } finally {
    workerProcess.kill('SIGTERM');
  }
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
