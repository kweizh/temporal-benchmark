import * as fs from 'fs';
import * as path from 'path';
import { Connection, Client } from '@temporalio/client';

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;
  if (!address || !namespace || !apiKey || !runId) {
    throw new Error('TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY, and ZEALT_RUN_ID must be set.');
  }

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
    metadata: { 'temporal-namespace': namespace },
  });
  const client = new Client({ connection, namespace });

  const workflowId = `retry-${runId}`;
  const result: string = await client.workflow.execute('FlakyWorkflow', {
    taskQueue: 'retry-ts',
    workflowId,
    args: [],
  });

  const line = `Workflow result: ${result}\n`;
  console.log(line.trimEnd());
  const logPath = path.join('/home/user/myproject', 'output.log');
  fs.appendFileSync(logPath, line);

  await connection.close();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
