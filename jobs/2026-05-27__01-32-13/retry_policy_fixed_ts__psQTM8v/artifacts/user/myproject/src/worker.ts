import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  if (!address || !namespace || !apiKey) {
    throw new Error('TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, and TEMPORAL_API_KEY must be set.');
  }

  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
    metadata: { 'temporal-namespace': namespace },
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'retry-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
