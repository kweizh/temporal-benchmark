import { NativeConnection, Worker } from '@temporalio/worker';
import { cleanup, doWork } from './activities';

const taskQueue = 'cancel-cleanup-ts';

export async function createWorker(): Promise<Worker> {
  const connection = await NativeConnection.connect({
    address: process.env.TEMPORAL_ADDRESS,
    apiKey: process.env.TEMPORAL_API_KEY,
    tls: true,
  });

  return Worker.create({
    connection,
    namespace: process.env.TEMPORAL_NAMESPACE,
    taskQueue,
    workflowsPath: require.resolve('./workflows'),
    activities: { doWork, cleanup },
  });
}
