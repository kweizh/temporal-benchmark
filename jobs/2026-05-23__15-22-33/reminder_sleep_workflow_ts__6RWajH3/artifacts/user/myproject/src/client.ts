import { Connection, Client } from '@temporalio/client';
import { ReminderWorkflow } from './workflows';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !namespace || !apiKey || !runId) {
    throw new Error('Missing environment variables for Temporal connection or ZEALT_RUN_ID');
  }

  const connection = await Connection.connect({
    address,
    tls: {
      apiKey,
    },
  });

  const client = new Client({
    connection,
    namespace,
  });

  const handle = await client.workflow.start(ReminderWorkflow, {
    taskQueue: 'reminder-ts',
    args: [{ message: 'wake up', delaySeconds: 3 }],
    workflowId: `reminder-${runId}`,
  });

  console.log(`Started workflow ${handle.workflowId}`);

  const result = await handle.result();
  console.log(result);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
