import { Connection, Client } from '@temporalio/client';
import { SubscriptionWorkflow, upgradeSignal, cancelSignal, getStatusQuery } from './workflows';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !namespace || !apiKey || !runId) {
    throw new Error('Missing Temporal environment variables');
  }

  const connection = await Connection.connect({
    address,
    apiKey,
    tls: true,
  });

  const client = new Client({
    connection,
    namespace,
  });

  const workflowId = `sub-${runId}`;

  const handle = await client.workflow.start(SubscriptionWorkflow, {
    taskQueue: 'sub-ts',
    workflowId,
    args: [{ userId: 'u1', tier: 'basic' }],
  });

  console.log(`Started workflow ${workflowId}`);

  // 1. After waiting 1 second of real time, sends the upgrade signal with argument "premium".
  await new Promise((resolve) => setTimeout(resolve, 1000));
  await handle.signal(upgradeSignal, 'premium');
  console.log('Sent upgrade signal');

  // 2. After waiting another 2 seconds of real time (so ~3 seconds since start), calls the getStatus query and logs the returned object to stdout.
  await new Promise((resolve) => setTimeout(resolve, 2000));
  const status = await handle.query(getStatusQuery);
  console.log(status);

  // 3. After waiting another 2 seconds of real time (so ~5 seconds since start), sends the cancel signal.
  await new Promise((resolve) => setTimeout(resolve, 2000));
  await handle.signal(cancelSignal);
  console.log('Sent cancel signal');

  // 4. Awaits the workflow's final result and prints it to stdout as Final result: <json>
  const result = await handle.result();
  console.log(`Final result: ${JSON.stringify(result)}`);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
