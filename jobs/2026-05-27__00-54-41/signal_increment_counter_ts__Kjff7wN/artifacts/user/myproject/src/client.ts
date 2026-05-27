import { Connection, Client } from '@temporalio/client';
import { CounterWorkflow, incrementSignal, finishSignal } from './workflows';
import * as dotenv from 'dotenv';
dotenv.config();

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID || 'local';

  if (!address || !apiKey || !namespace) {
    throw new Error('TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, and TEMPORAL_API_KEY must be set');
  }

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
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
