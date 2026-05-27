import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

async function run(): Promise<void> {
  const connection = await NativeConnection.connect({
    address: requireEnv('TEMPORAL_ADDRESS'),
    tls: true,
    apiKey: requireEnv('TEMPORAL_API_KEY')
  });

  const worker = await Worker.create({
    connection,
    namespace: requireEnv('TEMPORAL_NAMESPACE'),
    taskQueue: 'fetch-url-ts',
    workflowsPath: require.resolve('./workflows'),
    activities
  });

  await worker.run();
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
