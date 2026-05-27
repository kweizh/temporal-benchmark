import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';
import path from 'path';

const TASK_QUEUE = 'cancel-cleanup-ts';

async function main(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;

  if (!address) throw new Error('TEMPORAL_ADDRESS environment variable is required');
  if (!apiKey) throw new Error('TEMPORAL_API_KEY environment variable is required');
  if (!namespace) throw new Error('TEMPORAL_NAMESPACE environment variable is required');

  console.log(`[worker] Connecting to Temporal Cloud at ${address} (namespace: ${namespace})`);

  // NativeConnection for the Worker — connects with TLS + API key
  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: TASK_QUEUE,
    // Point at the compiled workflow bundle (workflow sandbox requires a path)
    workflowsPath: path.resolve(__dirname, './workflows'),
    activities,
  });

  console.log(`[worker] Worker created, polling task queue: ${TASK_QUEUE}`);
  // Signal the parent process (if any) that we are ready
  if (process.send) {
    process.send('ready');
  }
  // Also write to stdout so the orchestrator can detect readiness via output
  process.stdout.write('WORKER_READY\n');

  // Run until the process is interrupted
  await worker.run();
}

main().catch((err) => {
  console.error('[worker] Fatal error:', err);
  process.exit(1);
});
