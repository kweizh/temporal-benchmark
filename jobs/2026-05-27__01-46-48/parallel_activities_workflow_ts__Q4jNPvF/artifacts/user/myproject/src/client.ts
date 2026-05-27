/**
 * Temporal Client
 *
 * Connects to Temporal Cloud, starts ParallelSquaresWorkflow with the input
 * array [1, 2, 3, 4, 5], waits for the workflow to complete, and prints the
 * resulting sum to stdout.
 *
 * Credentials are read exclusively from environment variables:
 *   TEMPORAL_API_KEY      – API key issued by Temporal Cloud
 *   TEMPORAL_ADDRESS      – <namespace>.tmprl.cloud:7233 (or similar)
 *   TEMPORAL_NAMESPACE    – Temporal Cloud namespace
 *   ZEALT_RUN_ID          – Unique identifier for this run (used in workflow ID)
 */

import { Connection, Client } from '@temporalio/client';
import { ParallelSquaresWorkflow } from './workflows';

const TASK_QUEUE = 'parallel-squares-ts';
const INPUT      = [1, 2, 3, 4, 5];

async function main(): Promise<void> {
  const apiKey    = process.env.TEMPORAL_API_KEY;
  const address   = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const runId     = process.env.ZEALT_RUN_ID;

  if (!apiKey || !address || !namespace || !runId) {
    throw new Error(
      'Missing required environment variables: TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, ZEALT_RUN_ID'
    );
  }

  const workflowId = `parallel-wf-${runId}`;

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({
    connection,
    namespace,
  });

  console.log(`[client] Starting workflow "${workflowId}" with input: [${INPUT.join(', ')}]`);

  const result = await client.workflow.execute(ParallelSquaresWorkflow, {
    taskQueue: TASK_QUEUE,
    workflowId,
    args: [INPUT],
  });

  console.log(`[client] Workflow completed. Sum of squares: ${result}`);
}

main().catch((err) => {
  console.error('[client] Fatal error:', err);
  process.exit(1);
});
