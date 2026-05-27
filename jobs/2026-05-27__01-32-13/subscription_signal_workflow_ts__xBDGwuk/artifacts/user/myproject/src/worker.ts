import { NativeConnection, Worker } from '@temporalio/worker';
import { fileURLToPath } from 'node:url';
import * as activities from './activities.js';

const taskQueue = 'sub-ts';

export async function startWorker(): Promise<Worker> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;

  if (!address || !apiKey || !namespace) {
    throw new Error('Missing Temporal Cloud environment variables.');
  }

  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  return Worker.create({
    connection,
    namespace,
    taskQueue,
    workflowsPath: fileURLToPath(new URL('./workflows.ts', import.meta.url)),
    activities,
  });
}
