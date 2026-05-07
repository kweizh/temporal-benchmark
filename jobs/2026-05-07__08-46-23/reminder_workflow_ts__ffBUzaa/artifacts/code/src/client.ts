import { Connection, Client } from '@temporalio/client';
import { loadClientConnectConfig } from '@temporalio/envconfig';
import { reminderWorkflow } from './workflows';
import { randomUUID } from 'crypto';

async function run() {
  const config = await loadClientConnectConfig();

  const connection = await Connection.connect({
    address: config.address,
    tls: config.tls,
  });

  const client = new Client({
    connection,
    namespace: config.namespace,
  });

  const handle = await client.workflow.start(reminderWorkflow, {
    taskQueue: 'reminder-queue',
    workflowId: 'workflow-' + randomUUID(),
    args: [1000, 'Hello Temporal'],
  });

  console.log(`Started workflow ${handle.workflowId}`);

  const result = await handle.result();
  console.log(result);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
