import { Connection, Client, isCancellation } from '@temporalio/client';
import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';
import * as path from 'path';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID || 'local';
  const taskQueue = 'cancel-cleanup-ts';

  if (!address || !namespace || !apiKey) {
    throw new Error('Missing required environment variables: TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY');
  }

  // Connect to Temporal Cloud for Worker
  const workerConnection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection: workerConnection,
    namespace,
    taskQueue,
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  // Start the worker in the background
  const workerPromise = worker.run();
  console.log('Worker started');

  // Connect to Temporal Cloud for Client
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

  try {
    const handle = await client.workflow.start('CancellableWorkflow', {
      taskQueue,
      workflowId,
    });

    console.log(`Started workflow ${workflowId}`);

    // Wait 3 seconds then cancel
    await new Promise((resolve) => setTimeout(resolve, 3000));
    console.log(`Cancelling workflow ${workflowId}`);
    await handle.cancel();

    try {
      await handle.result();
    } catch (err) {
      if (isCancellation(err)) {
        console.log('cleanup-done observed');
      } else {
        console.error('Workflow failed with unexpected error:', err);
        process.exit(1);
      }
    }
  } catch (err) {
    console.error('Client failed:', err);
    process.exit(1);
  } finally {
    worker.shutdown();
    await workerPromise;
    await workerConnection.close();
    await clientConnection.close();
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
