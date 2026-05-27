import { Worker, NativeConnection } from '@temporalio/worker';
import * as activities from './activities';
import * as path from 'path';

const TEMPORAL_ADDRESS = process.env.TEMPORAL_ADDRESS!;
const TEMPORAL_API_KEY = process.env.TEMPORAL_API_KEY!;
const TEMPORAL_NAMESPACE = process.env.TEMPORAL_NAMESPACE!;

async function main() {
  const connection = await NativeConnection.connect({
    address: TEMPORAL_ADDRESS,
    tls: true,
    apiKey: TEMPORAL_API_KEY,
    metadata: {
      'temporal-namespace': TEMPORAL_NAMESPACE,
    },
  });

  const worker = await Worker.create({
    connection,
    namespace: TEMPORAL_NAMESPACE,
    taskQueue: 'progress-ts',
    workflowsPath: require.resolve('./workflow'),
    activities,
  });

  console.log('Worker started on task queue: progress-ts');
  await worker.run();
}

main().catch((err) => {
  console.error('Worker error:', err);
  process.exit(1);
});
