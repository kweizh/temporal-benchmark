import { Worker, NativeConnection } from '@temporalio/worker';
import { loadClientConnectConfig } from '@temporalio/envconfig';
import * as activities from './activities';

async function run() {
  const config = await loadClientConnectConfig();
  
  const connection = await NativeConnection.connect({
    address: config.address,
    tls: config.tls,
  });

  const worker = await Worker.create({
    connection,
    namespace: config.namespace,
    taskQueue: 'reminder-queue',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  console.log('Worker is running...');
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
