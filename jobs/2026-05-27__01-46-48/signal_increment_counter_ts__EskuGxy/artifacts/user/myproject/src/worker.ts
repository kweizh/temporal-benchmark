import { Worker, NativeConnection } from '@temporalio/worker';
import path from 'path';

async function run(): Promise<void> {
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
    taskQueue: 'counter-ts',
    workflowsPath: path.resolve(__dirname, '../src/workflows.ts'),
    activities: {},
  });

  console.log('Worker started, polling task queue: counter-ts');
  await worker.run();
}

run().catch((err) => {
  console.error('Worker error:', err);
  process.exit(1);
});
