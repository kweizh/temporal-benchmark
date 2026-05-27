import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';

function startWorker(): ChildProcess {
  const workerScript = path.join(__dirname, 'worker.js');
  const worker = spawn(process.execPath, [workerScript], {
    stdio: 'inherit',
    env: process.env,
  });
  worker.on('error', (err) => {
    console.error('Failed to start worker process:', err);
  });
  return worker;
}

async function runClient(): Promise<void> {
  return new Promise<void>((resolve, reject) => {
    const clientScript = path.join(__dirname, 'client.js');
    const client = spawn(process.execPath, [clientScript], {
      stdio: 'inherit',
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

async function main(): Promise<void> {
  const workerProcess = startWorker();

  // Give the worker a moment to connect and start polling before the client runs
  await new Promise<void>((resolve) => setTimeout(resolve, 3000));

  try {
    await runClient();
  } finally {
    // Shut down the worker once the client has finished
    workerProcess.kill('SIGTERM');
  }
}

main()
  .then(() => {
    process.exit(0);
  })
  .catch((err) => {
    console.error('Error:', err);
    process.exit(1);
  });
