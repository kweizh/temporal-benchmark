import { Client, Connection } from '@temporalio/client';

const TASK_QUEUE = 'child-workflow-ts';

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !apiKey || !namespace) {
    throw new Error('Missing TEMPORAL_ADDRESS, TEMPORAL_API_KEY, or TEMPORAL_NAMESPACE environment variables.');
  }

  if (!runId) {
    throw new Error('Missing ZEALT_RUN_ID environment variable.');
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

  const result = await client.workflow.execute('ParentSumWorkflow', {
    taskQueue: TASK_QUEUE,
    workflowId: `parent-wf-${runId}`,
    args: [[1, 2, 3]],
  });

  console.log(result);
}

run().catch((error) => {
  console.error('Client failed:', error);
  process.exit(1);
});
