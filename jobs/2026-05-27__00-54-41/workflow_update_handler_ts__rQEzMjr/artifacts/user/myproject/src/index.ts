import { NativeConnection, Worker } from '@temporalio/worker';
import { Connection, Client } from '@temporalio/client';
import { BankBalanceWorkflow } from './workflows';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE || 'default';
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID || 'test';
  
  const connectionOptions: any = {
    address,
  };
  
  if (apiKey) {
    connectionOptions.tls = true;
    connectionOptions.apiKey = apiKey;
  }

  const nativeConnection = await NativeConnection.connect(connectionOptions);
  const worker = await Worker.create({
    connection: nativeConnection,
    namespace,
    taskQueue: 'update-handler-ts',
    workflowsPath: require.resolve('./workflows'),
  });

  const clientConnection = await Connection.connect(connectionOptions);
  const client = new Client({
    connection: clientConnection,
    namespace,
  });

  const workerPromise = worker.run();

  try {
    const handle = await client.workflow.start(BankBalanceWorkflow, {
      taskQueue: 'update-handler-ts',
      workflowId: `update-wf-${runId}`,
    });

    const b1 = await handle.executeUpdate('deposit', { args: [100] });
    console.log(`Updated balance: ${b1}`);

    const b2 = await handle.executeUpdate('deposit', { args: [50] });
    console.log(`Updated balance: ${b2}`);

    const b3 = await handle.executeUpdate('deposit', { args: [25] });
    console.log(`Updated balance: ${b3}`);

    await handle.signal('finish');

    const finalBalance = await handle.result();
    console.log(`Final balance: ${finalBalance}`);
  } finally {
    worker.shutdown();
    await workerPromise;
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
