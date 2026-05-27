import { Worker, NativeConnection } from '@temporalio/worker';
import * as activities from './activities';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE || 'default';
  const apiKey = process.env.TEMPORAL_API_KEY;

  if (!address || !apiKey) {
    throw new Error('TEMPORAL_ADDRESS and TEMPORAL_API_KEY environment variables are required');
  }

  const connection = await NativeConnection.connect({
    address,
    metadata: {
      'api-key': apiKey,
    },
    tls: true,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'saga-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  console.log('Worker started, polling saga-ts task queue');
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
