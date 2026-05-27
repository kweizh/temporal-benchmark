import { Connection, Client } from '@temporalio/client';

async function run() {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  const connection = await Connection.connect({
    address: address!,
    tls: true,
    apiKey: apiKey!,
    metadata: { 'temporal-namespace': namespace! },
  });

  const client = new Client({ connection, namespace });
  const handle = client.workflow.getHandle(`discount-${runId}`);
  const description = await handle.describe();
  console.log(description.status);

  const history = await handle.fetchHistory();
  console.log(JSON.stringify(history, null, 2));
  
  await connection.close();
}

run().catch(console.error);