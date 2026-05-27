/**
 * client.ts
 *
 * Connects to Temporal Cloud, starts (or re-uses) a `FetchUrlWorkflow` execution,
 * waits for it to complete, and prints the activity result to stdout.
 *
 * Environment variables consumed:
 *   - TEMPORAL_ADDRESS   — host:port of the Temporal Cloud gRPC endpoint
 *   - TEMPORAL_API_KEY   — Temporal Cloud API key
 *   - TEMPORAL_NAMESPACE — target Temporal Cloud namespace
 *   - ZEALT_RUN_ID       — unique run identifier; incorporated into the Workflow ID
 *                          so that concurrent CI runs never collide.
 */

import { Client, Connection } from '@temporalio/client';
import { FetchUrlWorkflow } from './workflows';

const TASK_QUEUE = 'fetch-url-ts';
const TARGET_URL = 'https://api.github.com/zen';

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address) throw new Error('TEMPORAL_ADDRESS environment variable is required');
  if (!apiKey) throw new Error('TEMPORAL_API_KEY environment variable is required');
  if (!namespace) throw new Error('TEMPORAL_NAMESPACE environment variable is required');
  if (!runId) throw new Error('ZEALT_RUN_ID environment variable is required');

  // Connection.connect is the JS/gRPC connection used by the Client.
  // `tls: true` enables TLS; `apiKey` authenticates with Temporal Cloud.
  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({
    connection,
    namespace,
  });

  const workflowId = `fetch-wf-${runId}`;

  console.log(`[client] Starting workflow "${workflowId}" on task queue "${TASK_QUEUE}" ...`);
  console.log(`[client] Target URL: ${TARGET_URL}`);

  // `client.workflow.execute` starts the workflow and waits for its result in
  // a single call. It is equivalent to `start` followed by `handle.result()`.
  const result = await client.workflow.execute(FetchUrlWorkflow, {
    taskQueue: TASK_QUEUE,
    workflowId,
    args: [TARGET_URL],
  });

  // Print the activity result (the GitHub Zen API response body) to stdout.
  console.log(result);

  await connection.close();
}

run().catch((err) => {
  console.error('[client] Fatal error:', err);
  process.exit(1);
});
