import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} is required`);
  }
  return value;
}

async function runWorker(): Promise<void> {
  const connection = await NativeConnection.connect({
    address: requireEnv('TEMPORAL_ADDRESS'),
    tls: true,
    apiKey: requireEnv('TEMPORAL_API_KEY'),
  });

  const worker = await Worker.create({
    connection,
    namespace: requireEnv('TEMPORAL_NAMESPACE'),
    taskQueue: 'reminder-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  await worker.run();
}

runWorker().catch((error) => {
  console.error(error);
  process.exit(1);
});
