import { Connection, Client } from '@temporalio/client';
import { NativeConnection, Worker } from '@temporalio/worker';
import path from 'path';
import { BankBalanceWorkflow } from './workflows';

const taskQueue = 'update-handler-ts';

function getRequiredEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

async function runClient(): Promise<void> {
  const address = getRequiredEnv('TEMPORAL_ADDRESS');
  const apiKey = getRequiredEnv('TEMPORAL_API_KEY');
  const namespace = getRequiredEnv('TEMPORAL_NAMESPACE');
  const runId = getRequiredEnv('ZEALT_RUN_ID');

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({ connection, namespace });
  const workflowId = `update-wf-${runId}`;

  const handle = await client.workflow.start(BankBalanceWorkflow, {
    taskQueue,
    workflowId,
  });

  const amounts = [100, 50, 25];
  for (const amount of amounts) {
    const updatedBalance = await handle.executeUpdate<number>('deposit', {
      args: [amount],
    });
    console.log(`Updated balance: ${updatedBalance}`);
  }

  await handle.signal('finish');

  const finalBalance = await handle.result();
  console.log(`Final balance: ${finalBalance}`);
}

async function main(): Promise<void> {
  const address = getRequiredEnv('TEMPORAL_ADDRESS');
  const apiKey = getRequiredEnv('TEMPORAL_API_KEY');
  const namespace = getRequiredEnv('TEMPORAL_NAMESPACE');

  const workerConnection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const workflowsPath = require.resolve(path.join(__dirname, 'workflows'));

  const worker = await Worker.create({
    connection: workerConnection,
    namespace,
    taskQueue,
    workflowsPath,
  });

  const workerRun = worker.run();

  try {
    await runClient();
  } finally {
    worker.shutdown();
    await workerRun;
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
