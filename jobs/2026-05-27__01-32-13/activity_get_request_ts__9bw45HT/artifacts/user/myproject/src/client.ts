import { Connection, Client } from '@temporalio/client';
import { FetchUrlWorkflow } from './workflows';

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

async function run(): Promise<void> {
  const runId = requireEnv('ZEALT_RUN_ID');
  const connection = await Connection.connect({
    address: requireEnv('TEMPORAL_ADDRESS'),
    tls: true,
    apiKey: requireEnv('TEMPORAL_API_KEY')
  });

  const client = new Client({
    connection,
    namespace: requireEnv('TEMPORAL_NAMESPACE')
  });

  const result = await client.workflow.execute(FetchUrlWorkflow, {
    args: ['https://api.github.com/zen'],
    taskQueue: 'fetch-url-ts',
    workflowId: `fetch-wf-${runId}`
  });

  console.log(result);
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
