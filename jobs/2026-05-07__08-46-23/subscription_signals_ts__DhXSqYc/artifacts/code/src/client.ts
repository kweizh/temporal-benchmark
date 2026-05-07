import { Connection, Client } from '@temporalio/client';
import { loadClientConnectConfig } from '@temporalio/envconfig';
import { subscriptionWorkflow, updateTierSignal, cancelSubscriptionSignal } from './workflows';
import * as fs from 'fs';
import * as path from 'path';

async function run() {
  const config = await loadClientConnectConfig();
  const connection = await Connection.connect(config);
  const client = new Client({ connection, namespace: config.namespace });

  const workflowId = 'subscription-workflow-' + Date.now();
  
  const handle = await client.workflow.start(subscriptionWorkflow, {
    args: [{ initialTier: 'basic', billingPeriodMs: 2000 }],
    taskQueue: 'subscription-queue',
    workflowId,
  });

  console.log(`Started workflow ${handle.workflowId}`);

  // Wait 1 second
  await new Promise((resolve) => setTimeout(resolve, 1000));
  
  // Send updateTierSignal
  console.log('Sending updateTierSignal: premium');
  await handle.signal(updateTierSignal, 'premium');

  // Wait 3 seconds
  await new Promise((resolve) => setTimeout(resolve, 3000));

  // Send cancelSubscriptionSignal
  console.log('Sending cancelSubscriptionSignal');
  await handle.signal(cancelSubscriptionSignal);

  const result = await handle.result();
  console.log(`Workflow result: ${result}`);

  const logPath = '/home/user/project/output.log';
  fs.writeFileSync(logPath, result);
  console.log(`Result written to ${logPath}`);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
