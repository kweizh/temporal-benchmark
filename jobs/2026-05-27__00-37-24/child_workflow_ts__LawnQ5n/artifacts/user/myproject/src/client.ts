import { Connection, Client } from '@temporalio/client';
import { ParentSumWorkflow } from './workflows';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !namespace || !apiKey) {
    console.error('Missing TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, or TEMPORAL_API_KEY');
    process.exit(1);
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

  const handle = await client.workflow.start(ParentSumWorkflow, {
    taskQueue: 'child-workflow-ts',
    args: [[1, 2, 3]],
    workflowId: `parent-wf-${runId}`,
  });

  // Wait for the result
  const result = await handle.result();
  console.log(result);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
