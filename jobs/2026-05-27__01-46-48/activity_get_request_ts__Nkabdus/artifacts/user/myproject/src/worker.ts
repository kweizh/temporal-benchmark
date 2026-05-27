/**
 * worker.ts
 *
 * Registers the Workflow and Activity implementations with Temporal Cloud and
 * begins polling the `fetch-url-ts` task queue.
 *
 * Connection options:
 *   - TEMPORAL_ADDRESS   — host:port of the Temporal Cloud gRPC endpoint
 *   - TEMPORAL_API_KEY   — Temporal Cloud API key (used in place of mTLS certs)
 *   - TEMPORAL_NAMESPACE — the target Temporal Cloud namespace
 */

import { Worker, NativeConnection } from '@temporalio/worker';
import * as activities from './activities';
import path from 'path';

const TASK_QUEUE = 'fetch-url-ts';

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;

  if (!address) throw new Error('TEMPORAL_ADDRESS environment variable is required');
  if (!apiKey) throw new Error('TEMPORAL_API_KEY environment variable is required');
  if (!namespace) throw new Error('TEMPORAL_NAMESPACE environment variable is required');

  // NativeConnection is the Rust-backed gRPC connection used by the Worker.
  // `tls: true` enables TLS (required for Temporal Cloud).
  // The API key is passed as metadata that Temporal Cloud accepts in lieu of mTLS certificates.
  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: TASK_QUEUE,

    // `workflowsPath` points to the compiled (or ts-node interpreted) workflow
    // module. The Worker SDK automatically bundles it with webpack so that the
    // deterministic sandbox has no access to Node.js built-ins.
    workflowsPath: require.resolve('./workflows'),

    // The activities object maps activity type names to their implementations.
    // The SDK derives the activity type name from the exported function name,
    // so `fetchData` here becomes the "fetchData" activity type in Temporal.
    activities,
  });

  console.log(`[worker] Polling task queue "${TASK_QUEUE}" on namespace "${namespace}" ...`);

  // worker.run() resolves only when the worker is shut down (e.g. SIGINT/SIGTERM).
  await worker.run();
}

run().catch((err) => {
  console.error('[worker] Fatal error:', err);
  process.exit(1);
});
