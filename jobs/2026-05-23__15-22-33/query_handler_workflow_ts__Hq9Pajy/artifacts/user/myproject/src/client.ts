import { Connection, Client } from '@temporalio/client';
import { ProgressWorkflow, getProgressQuery } from './workflows.js';
import * as fs from 'fs';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !apiKey || !namespace || !runId) {
    throw new Error('Missing environment variables');
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

  const workflowId = `progress-${runId}`;

  const handle = await client.workflow.start(ProgressWorkflow, {
    taskQueue: 'progress-ts',
    workflowId,
    args: [5],
  });

  console.log(`Started workflow ${workflowId}`);

  // Wait approximately 2.5 seconds
  await new Promise((resolve) => setTimeout(resolve, 2500));

  // Send getProgress Query
  const queryResult = await handle.query(getProgressQuery);
  console.log('Query result:', queryResult);

  // Write query result to /workspace/progress.json
  fs.writeFileSync('/workspace/progress.json', JSON.stringify(queryResult, null, 2));

  // Await the final workflow result
  const result = await handle.result();
  console.log('Workflow result:', result);

  if (result.progress !== 1 || result.currentStep !== 5 || result.total !== 5) {
    throw new Error(`Unexpected result: ${JSON.stringify(result)}`);
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
