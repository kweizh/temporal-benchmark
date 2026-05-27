import { Worker, NativeConnection } from '@temporalio/worker';
import * as activities from './activities';
import * as path from 'path';

async function main() {
  const apiKey = process.env.TEMPORAL_API_KEY;
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;

  if (!apiKey || !address || !namespace) {
    throw new Error(
      'Missing required environment variables: TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE'
    );
  }

  // Connect to Temporal Cloud using API key + TLS
  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'sub-ts',
    // workflowsPath must point to the TypeScript source so the Temporal
    // worker can bundle it with webpack into a deterministic sandbox.
    // We go up from lib/ to src/ at runtime.
    workflowsPath: path.resolve(__dirname, '..', 'src', 'workflow.ts'),
    activities,
  });

  console.log('Worker started, polling task queue: sub-ts');

  // Run until cancelled
  await worker.run();
}

main().catch((err) => {
  console.error('Worker failed:', err);
  process.exit(1);
});
