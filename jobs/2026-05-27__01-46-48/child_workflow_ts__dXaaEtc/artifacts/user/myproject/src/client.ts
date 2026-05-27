import { Connection, Client } from '@temporalio/client';
import { ParentSumWorkflow } from './workflows';

async function main() {
  const apiKey = process.env.TEMPORAL_API_KEY;
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const runId = process.env.ZEALT_RUN_ID ?? `local-${Date.now()}`;

  if (!apiKey) throw new Error('TEMPORAL_API_KEY environment variable is required');
  if (!address) throw new Error('TEMPORAL_ADDRESS environment variable is required');
  if (!namespace) throw new Error('TEMPORAL_NAMESPACE environment variable is required');

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({
    connection,
    namespace,
  });

  const workflowId = `parent-wf-${runId}`;
  const input = [1, 2, 3];

  console.log(`[Client] Starting ParentSumWorkflow (id=${workflowId}) with input: [${input}]`);

  const result = await client.workflow.execute(ParentSumWorkflow, {
    taskQueue: 'child-workflow-ts',
    workflowId,
    args: [input],
  });

  console.log(result);
}

main().catch((err) => {
  console.error('[Client] Fatal error:', err);
  process.exit(1);
});
