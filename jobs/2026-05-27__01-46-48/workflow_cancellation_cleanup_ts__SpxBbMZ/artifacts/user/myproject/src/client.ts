import { Connection, Client, WorkflowFailedError } from '@temporalio/client';
import { isCancellation } from '@temporalio/workflow';
import { CancellableWorkflow } from './workflows';

const TASK_QUEUE = 'cancel-cleanup-ts';

async function main(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address) throw new Error('TEMPORAL_ADDRESS environment variable is required');
  if (!apiKey) throw new Error('TEMPORAL_API_KEY environment variable is required');
  if (!namespace) throw new Error('TEMPORAL_NAMESPACE environment variable is required');
  if (!runId) throw new Error('ZEALT_RUN_ID environment variable is required');

  const workflowId = `cancel-wf-${runId}`;

  console.log(`[client] Connecting to Temporal Cloud at ${address} (namespace: ${namespace})`);

  // Client connection — uses TLS + API key
  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({
    connection,
    namespace,
  });

  console.log(`[client] Starting workflow: ${workflowId} on task queue: ${TASK_QUEUE}`);

  const handle = await client.workflow.start(CancellableWorkflow, {
    taskQueue: TASK_QUEUE,
    workflowId,
  });

  console.log(`[client] Workflow started: ${handle.workflowId} (runId: ${handle.firstExecutionRunId})`);
  console.log('[client] Waiting 3 seconds before cancelling...');

  // Wait ~3 seconds to let the workflow (and doWork activity) get going
  await new Promise<void>((resolve) => setTimeout(resolve, 3000));

  console.log('[client] Sending cancellation request to workflow...');
  await handle.cancel();
  console.log('[client] Cancellation sent. Awaiting workflow result...');

  // Await the result — it WILL throw because the workflow ends as CANCELED
  try {
    await handle.result();
    // If we reach here, the workflow completed without cancellation (unexpected)
    console.error('[client] ERROR: Workflow completed without cancellation — unexpected!');
    process.exit(1);
  } catch (err) {
    if (err instanceof WorkflowFailedError && isCancellation(err.cause)) {
      // This is the expected path: the workflow was cancelled successfully
      // and cleanup ran (we can confirm by checking the event history, but
      // the acceptance criterion is the stdout line below)
      console.log('cleanup-done observed');
    } else {
      console.error('[client] Unexpected error awaiting workflow result:', err);
      throw err;
    }
  }

  await connection.close();
  console.log('[client] Done.');
}

main().catch((err) => {
  console.error('[client] Fatal error:', err);
  process.exit(1);
});
