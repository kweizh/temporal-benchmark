import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';

async function main() {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  if (!address || !apiKey || !namespace) {
    throw new Error('Missing TEMPORAL_ADDRESS / TEMPORAL_API_KEY / TEMPORAL_NAMESPACE');
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
    taskQueue: 'order-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  console.log('Worker started');
  await worker.run();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
