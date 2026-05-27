import { Connection, Client } from '@temporalio/client';
import { BankBalanceWorkflow, depositUpdate, finishSignal } from './workflows';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !namespace || !apiKey || !runId) {
    throw new Error('Missing environment variables');
  }

  const connection = await Connection.connect({
    address,
    tls: {
      apiKey,
    },
  });

  const client = new Client({
    connection,
    namespace,
  });

  const workflowId = `update-wf-${runId}`;

  const handle = await client.workflow.start(BankBalanceWorkflow, {
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
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
