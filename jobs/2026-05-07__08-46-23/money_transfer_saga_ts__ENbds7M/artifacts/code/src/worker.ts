import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS || 'localhost:7233';
  const namespace = process.env.TEMPORAL_NAMESPACE || 'default';
  const apiKey = process.env.TEMPORAL_API_KEY;

  const connection = await NativeConnection.connect({
    address,
    metadata: apiKey ? { authorization: `Bearer ${apiKey}` } : undefined,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'money-transfer-queue',
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
