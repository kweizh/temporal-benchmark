import { Client, Connection } from '@temporalio/client';

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} is required`);
  }
  return value;
}

export async function runClient(): Promise<string> {
  const connection = await Connection.connect({
    address: requireEnv('TEMPORAL_ADDRESS'),
    tls: true,
    apiKey: requireEnv('TEMPORAL_API_KEY'),
  });

  const client = new Client({
    connection,
    namespace: requireEnv('TEMPORAL_NAMESPACE'),
  });

  const workflowId = `reminder-${requireEnv('ZEALT_RUN_ID')}`;

  const result = await client.workflow.execute('ReminderWorkflow', {
    taskQueue: 'reminder-ts',
    workflowId,
    args: [{ message: 'wake up', delaySeconds: 3 }],
  });

  return result;
}

if (require.main === module) {
  runClient()
    .then((result) => {
      console.log(result);
    })
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
}
