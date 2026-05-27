import * as fs from 'fs';
import * as path from 'path';
import { Connection, Client } from '@temporalio/client';
import { DiscountWorkflow, DiscountResult } from './workflows';

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;
  if (!address || !namespace || !apiKey) {
    throw new Error('TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, and TEMPORAL_API_KEY must be set');
  }
  if (!runId) {
    throw new Error('ZEALT_RUN_ID must be set');
  }

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
    metadata: { 'temporal-namespace': namespace },
  });

  try {
    const client = new Client({ connection, namespace });
    const workflowId = `discount-${runId}`;
    let handle;
    try {
      handle = await client.workflow.start(DiscountWorkflow, {
        args: ['user-42'],
        taskQueue: 'discount-ts',
        workflowId,
      });
      console.log(`Started workflow ${handle.workflowId}`);
    } catch (err: any) {
      if (err.name === 'WorkflowExecutionAlreadyStartedError') {
        console.log(`Workflow ${workflowId} already started, getting handle...`);
        handle = client.workflow.getHandle(workflowId);
      } else {
        throw err;
      }
    }
    const result: DiscountResult = await handle.result();
    console.log('Workflow result:', JSON.stringify(result));
    const logFile = path.resolve(__dirname, '..', 'output.log');
    fs.appendFileSync(logFile, `Discount: ${result.discount}\n`);
  } finally {
    await connection.close();
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
