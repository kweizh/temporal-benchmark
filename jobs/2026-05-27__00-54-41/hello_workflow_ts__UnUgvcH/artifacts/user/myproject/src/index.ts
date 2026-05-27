import { NativeConnection, Worker } from '@temporalio/worker';
import { Connection, Client } from '@temporalio/client';
import * as activities from './activities';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE || 'default';
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !apiKey || !runId || !namespace) {
    throw new Error("Missing required environment variables: TEMPORAL_ADDRESS, TEMPORAL_API_KEY, TEMPORAL_NAMESPACE, ZEALT_RUN_ID");
  }

  // Connection Options for Temporal Cloud
  const connectionOptions = {
    address,
    tls: true,
    apiKey,
  };

  // 1. Establish Worker Connection
  const nativeConnection = await NativeConnection.connect(connectionOptions);
  
  // 2. Create the Worker
  const worker = await Worker.create({
    connection: nativeConnection,
    namespace,
    taskQueue: 'hello-world-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  // 3. Start worker in background
  const workerPromise = worker.run();

  // 4. Establish Client Connection
  const clientConnection = await Connection.connect(connectionOptions);
  
  // 5. Create the Client
  const client = new Client({
    connection: clientConnection,
    namespace,
  });

  const workflowId = `hello-wf-${runId}`;

  // 6. Start the Workflow
  const handle = await client.workflow.start('HelloWorkflow', {
    taskQueue: 'hello-world-ts',
    workflowId,
    args: ['Temporal'],
  });

  // 7. Wait for Workflow completion
  const result = await handle.result();
  
  // 8. Print result to stdout
  console.log(result);

  // 9. Shutdown worker gracefully
  worker.shutdown();
  await workerPromise;
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});