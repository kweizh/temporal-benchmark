import { Connection, Client } from '@temporalio/client';
import { loadClientConnectConfig } from '@temporalio/envconfig';
import { exampleWorkflow } from './workflows';

async function run() {
  const { connectionOptions, namespace } = loadClientConnectConfig();

  const connection = await Connection.connect(connectionOptions as any);

  const client = new Client({
    connection,
    namespace,
  });

  const handle = await client.workflow.start(exampleWorkflow, {
    taskQueue: 'tutorial',
    workflowId: 'workflow-' + Math.random().toString(36).substring(7),
  });

  console.log(`Started workflow ${handle.workflowId}`);

  const result = await handle.result();
  console.log('Workflow result:', JSON.stringify(result, null, 2));
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
