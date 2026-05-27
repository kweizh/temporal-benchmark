import { Connection, Client } from '@temporalio/client';
import { ParallelSquaresWorkflow } from './workflows';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !namespace || !apiKey || !runId) {
    throw new Error('Missing environment variables for Temporal Cloud');
  }

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({
    connection,
    namespace,
  });

  const workflowId = `parallel-wf-${runId}`;

  const handle = await client.workflow.start(ParallelSquaresWorkflow, {
    taskQueue: 'parallel-squares-ts',
    workflowId,
    args: [[1, 2, 3, 4, 5]],
  });

  console.log(`Started workflow ${workflowId}`);

  const result = await handle.result();
  console.log(result);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
