import { Connection, Client } from '@temporalio/client';
import { ProgressWorkflow, getProgress } from './workflows';
import * as fs from 'fs';

async function run() {
  const connection = await Connection.connect({
    address: process.env.TEMPORAL_ADDRESS,
    tls: true,
    metadata: {
      'temporal-namespace': process.env.TEMPORAL_NAMESPACE || 'default'
    },
    apiKey: process.env.TEMPORAL_API_KEY
  });

  const client = new Client({
    connection,
    namespace: process.env.TEMPORAL_NAMESPACE || 'default',
  });

  const runId = process.env.ZEALT_RUN_ID;
  if (!runId) {
    throw new Error('ZEALT_RUN_ID is not set');
  }

  const handle = await client.workflow.start(ProgressWorkflow, {
    args: [5],
    taskQueue: 'progress-ts',
    workflowId: `progress-${runId}`,
  });

  console.log(`Started workflow ${handle.workflowId}`);

  // Wait 2.5 seconds to query mid-run
  await new Promise((resolve) => setTimeout(resolve, 2500));

  const progress = await handle.query(getProgress);
  console.log('Queried progress:', progress);
  fs.writeFileSync('/workspace/progress.json', JSON.stringify(progress, null, 2));

  const result = await handle.result();
  console.log('Workflow result:', result);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});