import { Worker, NativeConnection } from '@temporalio/worker';
import { Connection, Client } from '@temporalio/client';
import * as workflows from './workflows';
import { depositUpdate, finishSignal } from './workflows';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !namespace || !apiKey || !runId) {
    throw new Error('Missing environment variables');
  }

  // Start Worker
  const nativeConnection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection: nativeConnection,
    namespace,
    taskQueue: 'update-handler-ts',
    workflowsPath: require.resolve('./workflows'),
  });

  const workerPromise = worker.run();
  console.log('Worker started');

  // Start Client
  try {
    const connection = await Connection.connect({
      address,
      tls: true,
      apiKey,
    });

    const client = new Client({
      connection,
      namespace,
    });

    const workflowId = `update-wf-${runId}`;

    const handle = await client.workflow.start(workflows.BankBalanceWorkflow, {
      taskQueue: 'update-handler-ts',
      workflowId,
    });

    const amounts = [100, 50, 25];
    for (const amount of amounts) {
      const balance = await handle.executeUpdate(depositUpdate, {
        args: [amount],
      });
      console.log(`Updated balance: ${balance}`);
    }

    await handle.signal(finishSignal);
    const result = await handle.result();
    console.log(`Final balance: ${result}`);

  } finally {
    worker.shutdown();
    await workerPromise;
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
