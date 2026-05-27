/**
 * start.ts — orchestrates Worker (background child process) + Client (in-process).
 *
 * 1. Spawns the worker as a child process.
 * 2. Waits for the worker to connect and start polling.
 * 3. Runs the client logic in-process to start the workflow and await its result.
 * 4. Prints the result, then kills the worker child process and exits.
 */
import { spawn } from 'child_process';
import * as path from 'path';
import { main as runClient } from './client-main';

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function run(): Promise<void> {
  const workerScript = path.join(__dirname, 'worker.js');

  // Spawn worker as a separate OS process so it can run concurrently
  const workerProcess = spawn(process.execPath, [workerScript], {
    stdio: 'inherit',
    env: process.env,
  });

  workerProcess.on('error', (err) => {
    console.error('Worker process error:', err);
  });

  // Give the worker time to establish the Temporal Cloud connection and begin polling
  await delay(4000);

  try {
    // Run the client: starts the workflow, waits for result, prints it
    await runClient();
  } finally {
    // Cleanly shut down the worker child process
    workerProcess.kill('SIGTERM');
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
