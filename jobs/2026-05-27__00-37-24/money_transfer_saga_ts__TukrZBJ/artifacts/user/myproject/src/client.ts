import { Connection, Client } from '@temporalio/client';
import { MoneyTransfer } from './workflows';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE || 'default';
  const apiKey = process.env.TEMPORAL_API_KEY;
  const zealtRunId = process.env.ZEALT_RUN_ID;

  if (!address || !apiKey || !zealtRunId) {
    throw new Error('TEMPORAL_ADDRESS, TEMPORAL_API_KEY, and ZEALT_RUN_ID environment variables are required');
  }

  const connection = await Connection.connect({
    address,
    metadata: {
      'api-key': apiKey,
    },
    tls: true,
  });

  const client = new Client({
    connection,
    namespace,
  });

  console.log('--- Starting Success Path Workflow ---');
  const okWorkflowId = `saga-ok-${zealtRunId}`;
  const handleOk = await client.workflow.start(MoneyTransfer, {
    taskQueue: 'saga-ts',
    workflowId: okWorkflowId,
    args: [{ fromAccount: 'A', toAccount: 'B', amount: 30 }],
  });
  console.log(`Started workflow ${okWorkflowId}`);
  await handleOk.result();
  console.log(`Workflow ${okWorkflowId} completed successfully`);

  console.log('\n--- Starting Failure Path Workflow ---');
  const failWorkflowId = `saga-fail-${zealtRunId}`;
  const handleFail = await client.workflow.start(MoneyTransfer, {
    taskQueue: 'saga-ts',
    workflowId: failWorkflowId,
    args: [{ fromAccount: 'A', toAccount: 'B_FAIL', amount: 50 }],
  });
  console.log(`Started workflow ${failWorkflowId}`);
  
  try {
    await handleFail.result();
    console.log(`Workflow ${failWorkflowId} unexpectedly completed successfully`);
  } catch (err) {
    console.log(`Workflow ${failWorkflowId} failed as expected: ${err}`);
  }

  console.log('\nSummary:');
  console.log(`- ${okWorkflowId}: COMPLETED`);
  console.log(`- ${failWorkflowId}: FAILED (Compensated)`);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
