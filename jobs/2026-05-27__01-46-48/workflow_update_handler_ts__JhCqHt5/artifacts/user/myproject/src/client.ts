import { Client, Connection } from '@temporalio/client';
import { BankBalanceWorkflow, depositUpdate, finishSignal } from './workflow';

async function main(): Promise<void> {
  const apiKey = process.env.TEMPORAL_API_KEY;
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const runId = process.env.ZEALT_RUN_ID;

  if (!apiKey || !address || !namespace || !runId) {
    throw new Error(
      'Missing required environment variables: TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, ZEALT_RUN_ID'
    );
  }

  const workflowId = `update-wf-${runId}`;

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({
    connection,
    namespace,
  });

  // Start the BankBalanceWorkflow; terminate any prior run with the same ID
  const handle = await client.workflow.start(BankBalanceWorkflow, {
    taskQueue: 'update-handler-ts',
    workflowId,
    workflowIdConflictPolicy: 'TERMINATE_EXISTING',
  });

  console.log(`Workflow started with ID: ${workflowId}`);

  // Send three deposit updates and print the returned new balance for each
  const amounts = [100, 50, 25];
  for (const amount of amounts) {
    const newBalance = await handle.executeUpdate(depositUpdate, {
      args: [amount],
    });
    console.log(`Updated balance: ${newBalance}`);
  }

  // Send the finish signal
  await handle.signal(finishSignal);

  // Await the workflow's final result
  const finalBalance = await handle.result();
  console.log(`Final balance: ${finalBalance}`);

  await connection.close();
}

main().catch((err) => {
  console.error('Client error:', err);
  process.exit(1);
});
