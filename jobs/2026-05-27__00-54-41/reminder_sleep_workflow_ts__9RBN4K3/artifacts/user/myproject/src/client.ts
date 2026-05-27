import { Connection, Client } from '@temporalio/client';
import { ReminderWorkflow } from './workflows';

export async function runClient() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !namespace || !apiKey) {
    throw new Error('Missing Temporal Cloud environment variables');
  }

  if (!runId) {
    throw new Error('Missing ZEALT_RUN_ID environment variable');
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

  const handle = await client.workflow.start(ReminderWorkflow, {
    taskQueue: 'reminder-ts',
    workflowId: `reminder-${runId}`,
    args: [{ message: 'wake up', delaySeconds: 3 }],
  });

  const result = await handle.result();
  console.log(result);
  return result;
}
