import { Connection, Client } from '@temporalio/client';
import { loadClientConnectConfig } from '@temporalio/envconfig';
import { helloWorld } from './workflows';
import * as fs from 'fs';
import * as path from 'path';

async function run() {
  const { connectionOptions, namespace } = await loadClientConnectConfig();
  
  const connection = await Connection.connect(connectionOptions);

  const client = new Client({
    connection,
    namespace,
  });

  const handle = await client.workflow.start(helloWorld, {
    taskQueue: 'hello-world-queue',
    workflowId: 'hello-world-workflow-' + Date.now(),
    args: ['Temporal'],
  });

  console.log(`Started workflow ${handle.workflowId}`);

  const result = await handle.result();
  console.log(`Workflow result: ${result}`);

  const logPath = path.join(__dirname, '..', 'output.log');
  fs.writeFileSync(logPath, result);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
