/**
 * run.ts — Orchestration entrypoint for `npm start`.
 *
 * 1. Spawns the Worker in a background child process.
 * 2. Waits briefly for the Worker to connect and begin polling.
 * 3. Runs the Client, which starts ParentSumWorkflow and awaits its result.
 * 4. Prints the numeric result to stdout.
 * 5. Terminates the Worker process and exits cleanly.
 */
import { spawn, ChildProcess } from 'child_process';
import path from 'path';

function startWorker(): ChildProcess {
  const workerPath = path.resolve(__dirname, 'worker.js');
  const worker = spawn(process.execPath, [workerPath], {
    stdio: ['ignore', 'pipe', 'pipe'],
    env: process.env,
  });

  worker.stdout?.on('data', (data: Buffer) => {
    process.stdout.write(`[Worker stdout] ${data}`);
  });
  worker.stderr?.on('data', (data: Buffer) => {
    process.stderr.write(`[Worker stderr] ${data}`);
  });
  worker.on('error', (err) => {
    console.error('[run] Worker process error:', err);
  });

  return worker;
}

function runClient(): Promise<void> {
  return new Promise((resolve, reject) => {
    const clientPath = path.resolve(__dirname, 'client.js');
    const client = spawn(process.execPath, [clientPath], {
      stdio: ['ignore', 'inherit', 'inherit'],
      env: process.env,
    });

    client.on('error', reject);
    client.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Client process exited with code ${code}`));
      }
    });
  });
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const worker = startWorker();

  // Give the Worker a moment to connect and start polling before the Client fires.
  console.log('[run] Waiting for Worker to start...');
  await sleep(5000);

  try {
    await runClient();
  } finally {
    console.log('[run] Client finished — terminating Worker.');
    worker.kill('SIGTERM');

    // Allow the worker a moment to clean up before we exit.
    await sleep(1000);
    process.exit(0);
  }
}

main().catch((err) => {
  console.error('[run] Fatal error:', err);
  process.exit(1);
});
