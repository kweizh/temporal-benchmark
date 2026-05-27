/**
 * Orchestrator: starts the Worker, waits for it to be ready, then runs the
 * Client. Exits with code 0 after the client observes the cancellation.
 *
 * Run via: npm start  (node -r ts-node/register src/start.ts)
 */

import { spawn, ChildProcess } from 'child_process';
import path from 'path';

const WORKER_READY_SIGNAL = 'WORKER_READY';
// Maximum time to wait for the worker to emit WORKER_READY
const WORKER_READY_TIMEOUT_MS = 60_000;

/**
 * Spawn a ts-node child process.
 * Returns the child process. stdout/stderr are left as streams so the caller
 * can attach its own handlers.
 */
function spawnWorker(script: string): ChildProcess {
  return spawn(process.execPath, ['-r', 'ts-node/register', script], {
    env: process.env,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
}

/**
 * Wait until the worker's stdout contains WORKER_READY_SIGNAL.
 * Also forwards every line to the parent's stdout/stderr.
 */
function attachWorkerStreamsAndWaitReady(worker: ChildProcess): Promise<void> {
  return new Promise((resolve, reject) => {
    let ready = false;
    let stdoutBuf = '';

    const timer = setTimeout(() => {
      if (!ready) {
        reject(new Error(`Worker did not emit '${WORKER_READY_SIGNAL}' within ${WORKER_READY_TIMEOUT_MS}ms`));
      }
    }, WORKER_READY_TIMEOUT_MS);

    worker.stdout!.on('data', (chunk: Buffer) => {
      stdoutBuf += chunk.toString();
      // Forward lines
      const lines = stdoutBuf.split('\n');
      stdoutBuf = lines.pop()!; // keep incomplete last line in buffer
      for (const line of lines) {
        if (line.trim()) process.stdout.write(`[worker] ${line.trim()}\n`);
      }
      // Check for ready signal in the accumulated data
      if (!ready && (chunk.toString().includes(WORKER_READY_SIGNAL) || stdoutBuf.includes(WORKER_READY_SIGNAL))) {
        ready = true;
        clearTimeout(timer);
        resolve();
      }
    });

    worker.stderr!.on('data', (chunk: Buffer) => {
      const lines = chunk.toString().split('\n');
      for (const line of lines) {
        if (line.trim()) process.stderr.write(`[worker:err] ${line.trim()}\n`);
      }
    });

    worker.on('exit', (code) => {
      clearTimeout(timer);
      if (!ready) {
        reject(new Error(`Worker exited (code ${code}) before becoming ready`));
      }
    });
  });
}

/**
 * Run the client as a child process. Forwards its stdout/stderr and resolves
 * with its exit code.
 */
function runClient(script: string): Promise<number> {
  return new Promise((resolve, reject) => {
    const client = spawn(process.execPath, ['-r', 'ts-node/register', script], {
      env: process.env,
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let stdoutBuf = '';
    client.stdout!.on('data', (chunk: Buffer) => {
      stdoutBuf += chunk.toString();
      const lines = stdoutBuf.split('\n');
      stdoutBuf = lines.pop()!;
      for (const line of lines) {
        if (line.trim()) {
          // Write client stdout directly — "cleanup-done observed" must appear
          // in the combined stdout of npm start without any prefix.
          process.stdout.write(line.trim() + '\n');
        }
      }
    });

    client.stderr!.on('data', (chunk: Buffer) => {
      const lines = chunk.toString().split('\n');
      for (const line of lines) {
        if (line.trim()) process.stderr.write(`[client:err] ${line.trim()}\n`);
      }
    });

    client.on('exit', (code) => resolve(code ?? 0));
    client.on('error', reject);
  });
}

async function main(): Promise<void> {
  const workerScript = path.resolve(__dirname, 'worker.ts');
  const clientScript = path.resolve(__dirname, 'client.ts');

  console.log('[start] Spawning worker process...');
  const worker = spawnWorker(workerScript);

  try {
    console.log('[start] Waiting for worker to be ready...');
    await attachWorkerStreamsAndWaitReady(worker);
    console.log('[start] Worker is ready. Starting client...');
  } catch (err) {
    console.error('[start] Worker failed to become ready:', err);
    worker.kill('SIGTERM');
    process.exit(1);
  }

  let clientExitCode = 1;
  try {
    clientExitCode = await runClient(clientScript);
  } catch (err) {
    console.error('[start] Client process error:', err);
  }

  console.log(`[start] Client finished with exit code: ${clientExitCode}`);

  // Gracefully terminate the worker
  console.log('[start] Stopping worker (SIGTERM)...');
  worker.kill('SIGTERM');
  await new Promise<void>((resolve) => {
    const forceKill = setTimeout(() => {
      worker.kill('SIGKILL');
      resolve();
    }, 10_000);
    worker.on('exit', () => {
      clearTimeout(forceKill);
      resolve();
    });
  });

  console.log('[start] All processes exited cleanly.');
  process.exit(clientExitCode === 0 ? 0 : clientExitCode);
}

main().catch((err) => {
  console.error('[start] Unhandled error:', err);
  process.exit(1);
});
