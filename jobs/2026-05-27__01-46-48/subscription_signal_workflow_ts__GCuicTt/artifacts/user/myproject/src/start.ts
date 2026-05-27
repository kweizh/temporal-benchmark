import { spawn } from 'child_process';
import * as path from 'path';

async function main() {
  const workerScript = path.resolve(__dirname, 'worker.js');
  const clientScript = path.resolve(__dirname, 'client.js');

  // Start the worker in the background
  const workerProcess = spawn(process.execPath, [workerScript], {
    env: process.env,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  workerProcess.stdout?.on('data', (data: Buffer) => {
    process.stdout.write(`[worker] ${data}`);
  });
  workerProcess.stderr?.on('data', (data: Buffer) => {
    process.stderr.write(`[worker] ${data}`);
  });

  // Give the worker time to bundle workflows and connect (~15s for first bundle)
  await new Promise((resolve) => setTimeout(resolve, 15000));

  // Run the client
  const clientProcess = spawn(process.execPath, [clientScript], {
    env: process.env,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  clientProcess.stdout?.on('data', (data: Buffer) => {
    process.stdout.write(data);
  });
  clientProcess.stderr?.on('data', (data: Buffer) => {
    process.stderr.write(data);
  });

  // Wait for the client to finish
  const exitCode: number = await new Promise((resolve) => {
    clientProcess.on('close', (code: number | null) => {
      resolve(code ?? 0);
    });
  });

  // Kill the worker now that the client is done
  workerProcess.kill('SIGTERM');

  // Wait for worker to exit
  await new Promise<void>((resolve) => {
    workerProcess.on('close', () => resolve());
    // Give it a few seconds to clean up, then force-resolve
    setTimeout(resolve, 5000);
  });

  process.exit(exitCode);
}

main().catch((err) => {
  console.error('Start script failed:', err);
  process.exit(1);
});
