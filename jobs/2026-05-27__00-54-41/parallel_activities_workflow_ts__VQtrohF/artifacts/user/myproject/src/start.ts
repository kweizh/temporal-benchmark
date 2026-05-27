import { NativeConnection, Worker } from '@temporalio/worker';
import { Connection, Client } from '@temporalio/client';
import * as activities from './activities';
import path from 'path';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !namespace || !apiKey || !runId) {
    throw new Error('Missing required environment variables');
  }

  // Create Worker Connection
  const workerConnection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  // Create Worker
  const worker = await Worker.create({
    connection: workerConnection,
    namespace,
    taskQueue: 'parallel-squares-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  // Start Worker in background
  const workerPromise = worker.run();

  // Create Client Connection
  const clientConnection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({
    connection: clientConnection,
    namespace,
  });

  // Execute Workflow
  const handle = await client.workflow.start('ParallelSquaresWorkflow', {
    args: [[1, 2, 3, 4, 5]],
    taskQueue: 'parallel-squares-ts',
    workflowId: `parallel-wf-${runId}`,
  });

  const result = await handle.result();
  console.log(result);

  // Shutdown worker and exit
  worker.shutdown();
  await workerPromise;
  process.exit(0);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});