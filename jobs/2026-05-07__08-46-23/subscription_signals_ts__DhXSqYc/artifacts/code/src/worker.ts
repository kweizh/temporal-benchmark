import { Worker } from '@temporalio/worker';
import { loadClientConnectConfig } from '@temporalio/envconfig';
import * as activities from './activities';

async function run() {
  const config = await loadClientConnectConfig();
  
  const worker = await Worker.create({
    ...config,
    workflowsPath: require.resolve('./workflows'),
    activities,
    taskQueue: 'subscription-queue',
  });

  console.log('Worker started, polling subscription-queue');
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
