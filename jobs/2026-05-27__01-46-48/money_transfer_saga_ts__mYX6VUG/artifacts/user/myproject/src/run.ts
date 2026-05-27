/**
 * run.ts — Orchestrates the worker and client in a single Node process.
 *
 * Strategy:
 *   1. Start the Worker (non-blocking — it runs on its own async loop).
 *   2. Run the Client script which executes both workflows and waits for
 *      their terminal states.
 *   3. Shut the worker down gracefully.
 *   4. Exit with code 0.
 */

import { Worker, NativeConnection } from '@temporalio/worker';
import { Connection, Client, WorkflowFailedError } from '@temporalio/client';
import * as activities from './activities';
import { MoneyTransfer } from './workflows';
import path from 'path';

async function main(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !apiKey || !namespace) {
    throw new Error(
      'Missing required environment variables: TEMPORAL_ADDRESS, TEMPORAL_API_KEY, TEMPORAL_NAMESPACE',
    );
  }
  if (!runId) {
    throw new Error('Missing required environment variable: ZEALT_RUN_ID');
  }

  // -----------------------------------------------------------------------
  // 1. Start the Worker
  // -----------------------------------------------------------------------
  console.log(`[run] Connecting worker to Temporal Cloud at ${address} (namespace: ${namespace})`);

  const workerConnection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection: workerConnection,
    namespace,
    taskQueue: 'saga-ts',
    workflowsPath: path.resolve(__dirname, 'workflows'),
    activities,
  });

  console.log('[run] Worker created, starting poll loop...');

  // Run the worker in the background — do NOT await here.
  const workerRunPromise = worker.run();

  // Give the worker a moment to register itself before sending work.
  await new Promise((resolve) => setTimeout(resolve, 1500));

  // -----------------------------------------------------------------------
  // 2. Connect the Client
  // -----------------------------------------------------------------------
  console.log('[run] Connecting client...');

  const clientConnection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({ connection: clientConnection, namespace });

  // -----------------------------------------------------------------------
  // 3. Workflow 1 — Happy path: A → B, amount 30
  // -----------------------------------------------------------------------
  const okWorkflowId = `saga-ok-${runId}`;
  console.log(`\n[run] Starting workflow: ${okWorkflowId}`);

  const okHandle = await client.workflow.start(MoneyTransfer, {
    taskQueue: 'saga-ts',
    workflowId: okWorkflowId,
    args: [{ fromAccount: 'A', toAccount: 'B', amount: 30 }],
  });

  console.log(`[run] Waiting for ${okWorkflowId} to complete...`);
  await okHandle.result();
  console.log(`[run] ✅ ${okWorkflowId} reached COMPLETED`);

  // -----------------------------------------------------------------------
  // 4. Workflow 2 — Failure path: A → B_FAIL, amount 50
  // -----------------------------------------------------------------------
  const failWorkflowId = `saga-fail-${runId}`;
  console.log(`\n[run] Starting workflow: ${failWorkflowId}`);

  const failHandle = await client.workflow.start(MoneyTransfer, {
    taskQueue: 'saga-ts',
    workflowId: failWorkflowId,
    args: [{ fromAccount: 'A', toAccount: 'B_FAIL', amount: 50 }],
  });

  console.log(`[run] Waiting for ${failWorkflowId} to reach terminal state...`);
  try {
    await failHandle.result();
    console.warn(`[run] ⚠️  ${failWorkflowId} completed unexpectedly (expected FAILED)`);
  } catch (err) {
    if (err instanceof WorkflowFailedError) {
      console.log(`[run] ✅ ${failWorkflowId} reached FAILED as expected (compensation applied)`);
      console.log(`[run]    Cause: ${err.cause?.message ?? err.message}`);
    } else {
      throw err;
    }
  }

  // -----------------------------------------------------------------------
  // 5. Summary
  // -----------------------------------------------------------------------
  const fs = await import('fs');
  const accounts = JSON.parse(fs.readFileSync('/workspace/accounts.json', 'utf8'));
  console.log('\n[run] ─── Final account balances ───────────────────────────────');
  console.log(JSON.stringify(accounts, null, 2));
  console.log('[run] ────────────────────────────────────────────────────────────');

  // -----------------------------------------------------------------------
  // 6. Shut down the worker and exit
  // -----------------------------------------------------------------------
  console.log('[run] Shutting down worker...');
  worker.shutdown();
  await workerRunPromise;

  await clientConnection.close();
  console.log('[run] All done. Exiting with code 0.');
}

main().catch((err) => {
  console.error('[run] Fatal error:', err);
  process.exit(1);
});
