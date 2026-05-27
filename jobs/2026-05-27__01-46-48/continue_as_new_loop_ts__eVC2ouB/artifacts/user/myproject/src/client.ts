import { Connection, Client } from '@temporalio/client';
import { LongLoopWorkflow } from './workflows';

export async function runClient(): Promise<number> {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;
  if (!address || !namespace || !apiKey || !runId) {
    throw new Error(
      'TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY, and ZEALT_RUN_ID must be set',
    );
  }

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({ connection, namespace });

  const handle = await client.workflow.start(LongLoopWorkflow, {
    args: [0, 25],
    taskQueue: 'loop-ts',
    workflowId: `loop-${runId}`,
  });

  const result = await handle.result();
  console.log(`Final result: ${result}`);
  return result;
}
