import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';

export async function runWorker(): Promise<Worker> {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  if (!address || !namespace || !apiKey) {
    throw new Error(
      'TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, and TEMPORAL_API_KEY must be set',
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
    taskQueue: 'loop-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  return worker;
}
