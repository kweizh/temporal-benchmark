import { Client, Connection } from '@temporalio/client';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS || 'localhost:7233';
  const namespace = process.env.TEMPORAL_NAMESPACE || 'default';
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID || 'local';

  const connectionOptions: any = {
    address,
  };

  if (apiKey) {
    connectionOptions.tls = true;
    connectionOptions.apiKey = apiKey;
  }

  const connection = await Connection.connect(connectionOptions);

  const client = new Client({
    connection,
    namespace,
  });

  console.log('Starting success workflow...');
  const handleOk = await client.workflow.start('MoneyTransfer', {
    taskQueue: 'saga-ts',
    workflowId: `saga-ok-${runId}`,
    args: [{ fromAccount: 'A', toAccount: 'B', amount: 30 }],
  });
  
  await handleOk.result();
  console.log('Success workflow completed.');

  console.log('Starting failing workflow...');
  const handleFail = await client.workflow.start('MoneyTransfer', {
    taskQueue: 'saga-ts',
    workflowId: `saga-fail-${runId}`,
    args: [{ fromAccount: 'A', toAccount: 'B_FAIL', amount: 50 }],
  });

  try {
    await handleFail.result();
  } catch (err) {
    console.log('Failing workflow failed as expected.');
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
