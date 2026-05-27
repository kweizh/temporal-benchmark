import { NativeConnection, Worker } from '@temporalio/worker';
import * as workflows from './workflows';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;

  if (!address || !namespace || !apiKey) {
    console.error('Missing TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, or TEMPORAL_API_KEY');
    process.exit(1);
  }

  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'child-workflow-ts',
    workflowsPath: require.resolve('./workflows'),
  });

  console.log('Worker started on task queue: child-workflow-ts');
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
