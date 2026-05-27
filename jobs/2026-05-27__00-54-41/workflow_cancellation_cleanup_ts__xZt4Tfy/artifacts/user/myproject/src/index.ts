import { Connection, Client, WorkflowFailedError } from '@temporalio/client';
import { NativeConnection, Worker } from '@temporalio/worker';
import { isCancellation } from '@temporalio/workflow';
import * as activities from './activities';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE || 'default';
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID || 'local';

  if (!address || !apiKey) {
    console.error("Missing TEMPORAL_ADDRESS or TEMPORAL_API_KEY");
    process.exit(1);
  }

  const workerConnection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection: workerConnection,
    namespace,
    taskQueue: 'cancel-cleanup-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  const clientConnection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({
    connection: clientConnection,
    namespace,
  });

  const workflowId = `cancel-wf-${runId}`;

  const workerPromise = worker.run();

  await new Promise((resolve) => setTimeout(resolve, 2000));

  console.log('Starting workflow...');
  const handle = await client.workflow.start('CancellableWorkflow', {
    taskQueue: 'cancel-cleanup-ts',
    workflowId,
  });

  console.log('Waiting 3 seconds before cancelling...');
  await new Promise((resolve) => setTimeout(resolve, 3000));

  console.log('Cancelling workflow...');
  await handle.cancel();

  try {
    await handle.result();
  } catch (err) {
    if (isCancellation(err) || (err instanceof WorkflowFailedError && isCancellation(err.cause))) {
      console.log('cleanup-done observed');
    } else {
      console.error('Workflow failed with error', err);
      process.exit(1);
    }
  }

  worker.shutdown();
  await workerPromise;
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
