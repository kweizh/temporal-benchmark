import { Client, Connection } from '@temporalio/client';
import { isCancellation } from '@temporalio/workflow';

const taskQueue = 'cancel-cleanup-ts';

export async function runClient(): Promise<void> {
  const connection = await Connection.connect({
    address: process.env.TEMPORAL_ADDRESS,
    apiKey: process.env.TEMPORAL_API_KEY,
    tls: true,
  });

  const client = new Client({
    connection,
    namespace: process.env.TEMPORAL_NAMESPACE,
  });

  const runId = process.env.ZEALT_RUN_ID ?? 'missing-run-id';
  const workflowId = `cancel-wf-${runId}`;

  const handle = await client.workflow.start('CancellableWorkflow', {
    taskQueue,
    workflowId,
  });

  await new Promise((resolve) => setTimeout(resolve, 3000));
  await handle.cancel();

  try {
    await handle.result();
  } catch (err) {
    if (isCancellation(err)) {
      console.log('cleanup-done observed');
      return;
    }
    throw err;
  }
}
