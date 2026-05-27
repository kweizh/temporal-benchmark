import { Worker, NativeConnection } from '@temporalio/worker';
import { Client, Connection } from '@temporalio/client';
import { ParentSumWorkflow } from './workflows';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  if (!address) throw new Error("TEMPORAL_ADDRESS is required");
  const namespace = process.env.TEMPORAL_NAMESPACE;
  if (!namespace) throw new Error("TEMPORAL_NAMESPACE is required");
  const apiKey = process.env.TEMPORAL_API_KEY;
  if (!apiKey) throw new Error("TEMPORAL_API_KEY is required");
  const runId = process.env.ZEALT_RUN_ID || 'default-run-id';

  // Setup Worker
  const workerConnection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection: workerConnection,
    namespace,
    taskQueue: 'child-workflow-ts',
    workflowsPath: require.resolve('./workflows'),
  });

  const workerPromise = worker.run();

  // Setup Client
  const clientConnection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({
    connection: clientConnection,
    namespace,
  });

  try {
    const result = await client.workflow.execute(ParentSumWorkflow, {
      args: [[1, 2, 3]],
      taskQueue: 'child-workflow-ts',
      workflowId: `parent-wf-${runId}`,
    });
    console.log(result);
  } finally {
    worker.shutdown();
    await workerPromise;
  }
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
