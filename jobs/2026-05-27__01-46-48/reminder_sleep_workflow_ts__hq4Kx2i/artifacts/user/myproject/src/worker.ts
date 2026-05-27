import { Worker, NativeConnection } from '@temporalio/worker';
import * as activities from './activities';
import * as path from 'path';

async function main(): Promise<void> {
  const apiKey = process.env.TEMPORAL_API_KEY;
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;

  if (!apiKey || !address || !namespace) {
    throw new Error(
      'Missing required environment variables: TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE'
    );
  }

  // Connect to Temporal Cloud using API key + TLS
  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'reminder-ts',
    // Point the bundler at our compiled workflow file
    workflowsPath: path.join(__dirname, 'workflows'),
    activities,
  });

  console.log('Worker started, polling task queue "reminder-ts"...');
  await worker.run();
}

main().catch((err) => {
  console.error('Worker failed:', err);
  process.exit(1);
});
