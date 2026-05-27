import { Worker, NativeConnection } from '@temporalio/worker';
import * as path from 'path';

async function main(): Promise<void> {
  const apiKey = process.env.TEMPORAL_API_KEY;
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;

  if (!apiKey || !address || !namespace) {
    throw new Error(
      'Missing required environment variables: TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE'
    );
  }

  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'update-handler-ts',
    // workflowsPath must point to the TS source file so the Temporal bundler
    // can webpack it. __dirname inside dist/ => go up one level to src/
    workflowsPath: path.join(__dirname, '..', 'src', 'workflow.ts'),
  });

  console.log('Worker started, polling task queue: update-handler-ts');
  await worker.run();
}

main().catch((err) => {
  console.error('Worker error:', err);
  process.exit(1);
});
