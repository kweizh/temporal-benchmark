import { Connection, Client } from '@temporalio/client';
import { ProgressWorkflow, getProgressQuery } from './workflow';
import * as fs from 'fs';

const TEMPORAL_ADDRESS = process.env.TEMPORAL_ADDRESS!;
const TEMPORAL_API_KEY = process.env.TEMPORAL_API_KEY!;
const TEMPORAL_NAMESPACE = process.env.TEMPORAL_NAMESPACE!;
const ZEALT_RUN_ID = process.env.ZEALT_RUN_ID!;

async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const workflowId = `progress-${ZEALT_RUN_ID}`;

  const connection = await Connection.connect({
    address: TEMPORAL_ADDRESS,
    tls: true,
    apiKey: TEMPORAL_API_KEY,
    metadata: {
      'temporal-namespace': TEMPORAL_NAMESPACE,
    },
  });

  const client = new Client({
    connection,
    namespace: TEMPORAL_NAMESPACE,
  });

  console.log(`Starting workflow with id: ${workflowId}`);
  const handle = await client.workflow.start(ProgressWorkflow, {
    taskQueue: 'progress-ts',
    workflowId,
    args: [5],
  });

  console.log(`Workflow started. Waiting 2.5 seconds before querying...`);
  await sleep(2500);

  console.log('Sending getProgress query...');
  const progressResult = await handle.query(getProgressQuery);
  console.log('Query result:', progressResult);

  fs.writeFileSync('/workspace/progress.json', JSON.stringify(progressResult));
  console.log('Written progress.json:', progressResult);

  console.log('Awaiting final workflow result...');
  const finalResult = await handle.result();
  console.log('Final result:', finalResult);
}

main().catch((err) => {
  console.error('Client error:', err);
  process.exit(1);
});
