import { Connection, Client } from '@temporalio/client';
import { FetchUrlWorkflow } from './workflows';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const zealtRunId = process.env.ZEALT_RUN_ID || 'local';

  if (!address || !namespace || !apiKey) {
    throw new Error('Missing environment variables: TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, or TEMPORAL_API_KEY');
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

  const handle = await client.workflow.start(FetchUrlWorkflow, {
    taskQueue: 'fetch-url-ts',
    workflowId: `fetch-wf-${zealtRunId}`,
    args: ['https://api.github.com/zen'],
  });

  const result = await handle.result();
  process.stdout.write(result + '\n');
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
