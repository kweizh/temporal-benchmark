import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';
import path from 'path';

export async function runWorker(): Promise<void> {
  const apiKey = process.env.TEMPORAL_API_KEY;
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;

  if (!apiKey || !address || !namespace) {
    throw new Error(
      'Missing required environment variables: TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE'
    );
  }

  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'hello-world-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  console.log('Worker started, polling task queue: hello-world-ts');
  await worker.run();
}

// Allow direct execution: `node dist/worker.js`
if (require.main === module) {
  runWorker().catch((err) => {
    console.error('Worker failed:', err);
    process.exit(1);
  });
}
