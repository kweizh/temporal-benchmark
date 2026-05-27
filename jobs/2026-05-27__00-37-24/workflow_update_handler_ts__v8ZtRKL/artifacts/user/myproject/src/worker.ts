import { Worker, NativeConnection } from '@temporalio/worker';
import * as workflows from './workflows';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;

  if (!address || !namespace || !apiKey) {
    throw new Error('Missing Temporal Cloud credentials in environment variables');
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
    taskQueue: 'update-handler-ts',
    workflowsPath: require.resolve('./workflows'),
  });

  console.log('Worker started');
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
