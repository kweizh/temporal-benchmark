import { Connection, Client } from '@temporalio/client';
import { CounterWorkflow, incrementSignal, finishSignal } from './workflows';

async function run(): Promise<void> {
  const apiKey = process.env.TEMPORAL_API_KEY;
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const runId = process.env.ZEALT_RUN_ID;

  if (!apiKey || !address || !namespace) {
    throw new Error(
      'Missing required environment variables: TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE'
    );
  }

  if (!runId) {
    throw new Error('Missing required environment variable: ZEALT_RUN_ID');
  }

  const workflowId = `counter-wf-${runId}`;

  // Connect to Temporal Cloud
  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({
    connection,
    namespace,
  });

  // Start the CounterWorkflow
  const handle = await client.workflow.start(CounterWorkflow, {
    taskQueue: 'counter-ts',
    workflowId,
  });

  console.log(`Started workflow: ${workflowId}`);

  // Send increment signals: 5, 3, 2
  await handle.signal(incrementSignal, 5);
  console.log('Sent increment signal: 5');

  await handle.signal(incrementSignal, 3);
  console.log('Sent increment signal: 3');

  await handle.signal(incrementSignal, 2);
  console.log('Sent increment signal: 2');

  // Send finish signal
  await handle.signal(finishSignal);
  console.log('Sent finish signal');

  // Await the workflow result and print it
  const result = await handle.result();
  console.log(result);
}

run().catch((err) => {
  console.error('Client error:', err);
  process.exit(1);
});
