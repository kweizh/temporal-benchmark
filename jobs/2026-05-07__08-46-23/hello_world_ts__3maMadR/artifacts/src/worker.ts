import { Worker, NativeConnection } from '@temporalio/worker';
import { loadClientConnectConfig } from '@temporalio/envconfig';
import * as workflows from './workflows';

async function run() {
  const { connectionOptions, namespace } = await loadClientConnectConfig();
  
  const connection = await NativeConnection.connect(connectionOptions);

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'hello-world-queue',
    workflowsPath: require.resolve('./workflows'),
  });

  console.log('Worker started');
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
