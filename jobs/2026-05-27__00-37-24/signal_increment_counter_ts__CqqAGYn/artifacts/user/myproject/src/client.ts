import { Connection, Client } from '@temporalio/client';
import { CounterWorkflow, incrementSignal, finishSignal } from './workflows';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !namespace || !apiKey || !runId) {
    throw new Error('Missing required environment variables');
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

  const workflowId = `counter-wf-${runId}`;

  const handle = await client.workflow.start(CounterWorkflow, {
    taskQueue: 'counter-ts',
    workflowId,
  });

  console.log(`Started workflow ${workflowId}`);

  await handle.signal(incrementSignal, 5);
  await handle.signal(incrementSignal, 3);
  await handle.signal(incrementSignal, 2);
  await handle.signal(finishSignal);

  const result = await handle.result();
  console.log(result);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
