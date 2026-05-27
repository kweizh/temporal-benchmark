import { Connection, Client } from '@temporalio/client';

const taskQueue = 'sub-ts';

function getEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing environment variable: ${name}`);
  }
  return value;
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

export async function runClient(): Promise<void> {
  const address = getEnv('TEMPORAL_ADDRESS');
  const apiKey = getEnv('TEMPORAL_API_KEY');
  const namespace = getEnv('TEMPORAL_NAMESPACE');
  const runId = getEnv('ZEALT_RUN_ID');

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({ connection, namespace });

  const handle = await client.workflow.start('SubscriptionWorkflow', {
    taskQueue,
    workflowId: `sub-${runId}`,
    args: [{ userId: 'u1', tier: 'basic' }],
  });

  await delay(1000);
  await handle.signal('upgrade', 'premium');

  await delay(2000);
  const status = await handle.query('getStatus');
  console.log(status);

  await delay(2000);
  await handle.signal('cancel');

  const result = await handle.result();
  console.log(`Final result: ${JSON.stringify(result)}`);
}
