import { Worker, NativeConnection } from '@temporalio/worker';
import * as activities from './activities';
import path from 'path';

async function main(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;

  if (!address || !apiKey || !namespace) {
    throw new Error(
      'Missing required environment variables: TEMPORAL_ADDRESS, TEMPORAL_API_KEY, TEMPORAL_NAMESPACE',
    );
  }

  console.log(`[worker] Connecting to Temporal Cloud at ${address} (namespace: ${namespace})`);

  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'saga-ts',
    // Point at the compiled workflow bundle directory
    workflowsPath: path.resolve(__dirname, 'workflows'),
    activities,
  });

  console.log('[worker] Worker started, polling task queue "saga-ts"...');
  await worker.run();
}

main().catch((err) => {
  console.error('[worker] Fatal error:', err);
  process.exit(1);
});
