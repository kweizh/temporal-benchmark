import { NativeConnection, Worker } from '@temporalio/worker';
import { Connection, Client } from '@temporalio/client';
import { FetchUrlWorkflow } from './workflows';
import * as activities from './activities';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE || 'default';
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID || 'local';

  if (!address || !apiKey) {
    throw new Error("TEMPORAL_ADDRESS and TEMPORAL_API_KEY must be set");
  }

  const connectionOptions = {
    address,
    tls: true,
    apiKey,
  };

  // Worker Connection
  const workerConnection = await NativeConnection.connect(connectionOptions);

  const worker = await Worker.create({
    connection: workerConnection,
    namespace,
    taskQueue: 'fetch-url-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  const workerPromise = worker.run();

  // Client Connection
  const clientConnection = await Connection.connect(connectionOptions);

  const client = new Client({
    connection: clientConnection,
    namespace,
  });

  const workflowId = `fetch-wf-${runId}`;

  try {
    const handle = await client.workflow.start(FetchUrlWorkflow, {
      taskQueue: 'fetch-url-ts',
      workflowId,
      args: ['https://api.github.com/zen'],
    });

    const result = await handle.result();
    console.log(result);
  } finally {
    worker.shutdown();
    await workerPromise;
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
