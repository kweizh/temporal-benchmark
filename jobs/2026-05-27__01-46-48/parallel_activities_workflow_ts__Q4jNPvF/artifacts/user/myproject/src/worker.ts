/**
 * Temporal Worker
 *
 * Connects to Temporal Cloud using API-key auth, registers
 * ParallelSquaresWorkflow and the squareNumber activity, then starts polling
 * the `parallel-squares-ts` task queue.
 *
 * Credentials are read exclusively from environment variables:
 *   TEMPORAL_API_KEY      – API key issued by Temporal Cloud
 *   TEMPORAL_ADDRESS      – <namespace>.tmprl.cloud:7233 (or similar)
 *   TEMPORAL_NAMESPACE    – Temporal Cloud namespace
 */

import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';
import path from 'path';

const TASK_QUEUE = 'parallel-squares-ts';

async function main(): Promise<void> {
  const apiKey    = process.env.TEMPORAL_API_KEY;
  const address   = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;

  if (!apiKey || !address || !namespace) {
    throw new Error(
      'Missing required environment variables: TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE'
    );
  }

  // NativeConnection is required for the Worker (uses the Rust core under the hood).
  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: TASK_QUEUE,
    // workflowsPath must point to the compiled workflow module.
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  console.log(`[worker] Polling task queue "${TASK_QUEUE}" on namespace "${namespace}" …`);
  await worker.run();
}

main().catch((err) => {
  console.error('[worker] Fatal error:', err);
  process.exit(1);
});
