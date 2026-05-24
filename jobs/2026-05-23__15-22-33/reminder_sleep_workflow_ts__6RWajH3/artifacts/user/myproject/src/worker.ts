import { Worker, NativeConnection } from '@temporalio/worker';
import * as activities from './activities';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;

  if (!address || !namespace || !apiKey) {
    throw new Error('Missing environment variables for Temporal connection');
  }

  const connection = await NativeConnection.connect({
    address,
    tls: {
      apiKey,
    },
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'reminder-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  console.log('Worker started');
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
