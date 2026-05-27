import { Worker, NativeConnection } from '@temporalio/worker';
import * as activities from './activities';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS || 'localhost:7233';
  const namespace = process.env.TEMPORAL_NAMESPACE || 'default';
  const apiKey = process.env.TEMPORAL_API_KEY;

  const connectionOptions: any = {
    address,
  };

  if (apiKey) {
    connectionOptions.tls = true;
    connectionOptions.apiKey = apiKey;
  }

  const connection = await NativeConnection.connect(connectionOptions);

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'saga-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
