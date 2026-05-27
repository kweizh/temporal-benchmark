import { NativeConnection, Worker } from '@temporalio/worker';
import * as dotenv from 'dotenv';
dotenv.config();

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;

  if (!address || !apiKey || !namespace) {
    throw new Error('TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, and TEMPORAL_API_KEY must be set');
  }

  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'counter-ts',
    workflowsPath: require.resolve('./workflows'),
  });

  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
