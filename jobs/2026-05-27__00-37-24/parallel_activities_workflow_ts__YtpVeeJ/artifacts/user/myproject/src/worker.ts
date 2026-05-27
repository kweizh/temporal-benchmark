import { Worker, NativeConnection } from '@temporalio/worker';
import * as activities from './activities';

async function run() {
  console.log('Starting worker process...');
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;

  if (!address || !namespace || !apiKey) {
    throw new Error('Missing environment variables for Temporal Cloud');
  }

  console.log('Connecting to Temporal Cloud...');
  const connection = await NativeConnection.connect({
    address,
    tls: {
      clientCertPair: undefined, // Using API Key instead
    },
    metadata: {
      'authorization': `Bearer ${apiKey}`,
    },
  });
  console.log('Connected to NativeConnection');

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'parallel-squares-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  console.log('Worker started, polling parallel-squares-ts task queue');
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
