import { Connection, Client } from '@temporalio/client';
import { ReminderWorkflow } from './workflows';

export async function main(): Promise<void> {
  const apiKey = process.env.TEMPORAL_API_KEY;
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const runId = process.env.ZEALT_RUN_ID;

  if (!apiKey || !address || !namespace) {
    throw new Error(
      'Missing required environment variables: TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE'
    );
  }

  if (!runId) {
    throw new Error('Missing required environment variable: ZEALT_RUN_ID');
  }

  // Connect to Temporal Cloud using API key + TLS
  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({
    connection,
    namespace,
  });

  const workflowId = `reminder-${runId}`;

  console.log(`Starting ReminderWorkflow with ID: ${workflowId}`);

  const handle = await client.workflow.start(ReminderWorkflow, {
    taskQueue: 'reminder-ts',
    workflowId,
    args: [{ message: 'wake up', delaySeconds: 3 }],
  });

  console.log(`Workflow started, waiting for result...`);

  const result = await handle.result();
  console.log(result);

  await connection.close();
}
