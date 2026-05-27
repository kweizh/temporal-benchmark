import { spawn } from 'child_process';
import path from 'path';
import { runClient } from './client';

async function main(): Promise<void> {
  // Spawn the worker as a background child process
  const workerProcess = spawn(
    process.execPath,
    [path.join(__dirname, 'worker.js')],
    {
      env: process.env,
      stdio: ['ignore', 'pipe', 'pipe'],
      detached: false,
    }
  );

  workerProcess.stdout?.on('data', (data: Buffer) => {
    process.stdout.write(`[worker] ${data}`);
  });
  workerProcess.stderr?.on('data', (data: Buffer) => {
    process.stderr.write(`[worker] ${data}`);
  });

  workerProcess.on('error', (err) => {
    console.error('Worker process error:', err);
  });

  // Give the worker time to connect and start polling before the client fires
  await new Promise<void>((resolve) => setTimeout(resolve, 4000));

  try {
    await runClient();
  } finally {
    // Terminate the background worker cleanly after the workflow completes
    workerProcess.kill('SIGTERM');
    // Brief pause to allow process cleanup
    await new Promise<void>((resolve) => setTimeout(resolve, 500));
  }

  process.exit(0);
}

main().catch((err) => {
  console.error('Fatal error in start script:', err);
  process.exit(1);
});
