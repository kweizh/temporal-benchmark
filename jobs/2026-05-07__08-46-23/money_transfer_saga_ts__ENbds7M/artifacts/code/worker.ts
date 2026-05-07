import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';

async function run() {
  // Use environment variables provided by the user
  const address = process.env.TEMPORAL_ADDRESS || 'localhost:7233';
  const namespace = process.env.TEMPORAL_NAMESPACE || 'default';
  const apiKey = process.env.TEMPORAL_API_KEY;

  // Connection options for Temporal Cloud
  const connection = await NativeConnection.connect({
    address,
    metadata: apiKey ? { authorization: `Bearer ${apiKey}` } : undefined,
    // If using mTLS, cert and key would go here, but user specified API Key
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'money-transfer-queue',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  console.log(`Worker started on task queue: money-transfer-queue`);
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
