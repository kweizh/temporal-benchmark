import { Worker, NativeConnection } from '@temporalio/worker';
import { Connection, Client } from '@temporalio/client';
import { SubscriptionWorkflow } from './workflow';
import * as activities from './activities';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS || 'localhost:7233';
  const namespace = process.env.TEMPORAL_NAMESPACE || 'default';
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!runId) {
    throw new Error('ZEALT_RUN_ID is required');
  }

  // Common connection options for Temporal Cloud
  const connectionOptions = {
    address,
    tls: true,
    apiKey,
  };

  // 1. Setup Worker
  const workerConnection = await NativeConnection.connect(connectionOptions);
  
  const worker = await Worker.create({
    connection: workerConnection,
    namespace,
    taskQueue: 'sub-ts',
    workflowsPath: require.resolve('./workflow'),
    activities,
  });

  // Start worker in the background
  const workerPromise = worker.run();

  // 2. Setup Client
  const clientConnection = await Connection.connect(connectionOptions);
  const client = new Client({
    connection: clientConnection,
    namespace,
  });

  const workflowId = `sub-${runId}`;

  try {
    // Start workflow
    const handle = await client.workflow.start(SubscriptionWorkflow, {
      args: [{ userId: 'u1', tier: 'basic' }],
      taskQueue: 'sub-ts',
      workflowId,
    });

    // Wait 1 second of real time, send upgrade
    await new Promise(resolve => setTimeout(resolve, 1000));
    await handle.signal('upgrade', 'premium');

    // Wait 2 seconds of real time, call getStatus
    await new Promise(resolve => setTimeout(resolve, 2000));
    const status = await handle.query('getStatus');
    console.log(status);

    // Wait 2 seconds of real time, send cancel
    await new Promise(resolve => setTimeout(resolve, 2000));
    await handle.signal('cancel');

    // Await workflow's final result
    const result = await handle.result();
    console.log(`Final result: ${JSON.stringify(result)}`);
  } finally {
    worker.shutdown();
    await workerPromise;
  }
}

run().then(() => process.exit(0)).catch(err => {
  console.error(err);
  process.exit(1);
});
