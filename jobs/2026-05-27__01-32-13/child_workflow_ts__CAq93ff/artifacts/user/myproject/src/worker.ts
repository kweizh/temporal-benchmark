import { NativeConnection, Worker } from '@temporalio/worker';

const TASK_QUEUE = 'child-workflow-ts';

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;

  if (!address || !apiKey || !namespace) {
    throw new Error('Missing TEMPORAL_ADDRESS, TEMPORAL_API_KEY, or TEMPORAL_NAMESPACE environment variables.');
  }

  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: TASK_QUEUE,
    workflowsPath: require.resolve('./workflows'),
  });

  await worker.run();
}

run().catch((error) => {
  console.error('Worker failed:', error);
  process.exit(1);
});
