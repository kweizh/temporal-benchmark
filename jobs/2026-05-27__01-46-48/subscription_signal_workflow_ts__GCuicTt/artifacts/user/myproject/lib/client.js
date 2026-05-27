"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const client_1 = require("@temporalio/client");
const workflow_1 = require("./workflow");
function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
async function main() {
    const apiKey = process.env.TEMPORAL_API_KEY;
    const address = process.env.TEMPORAL_ADDRESS;
    const namespace = process.env.TEMPORAL_NAMESPACE;
    const runId = process.env.ZEALT_RUN_ID;
    if (!apiKey || !address || !namespace) {
        throw new Error('Missing required environment variables: TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE');
    }
    if (!runId) {
        throw new Error('Missing required environment variable: ZEALT_RUN_ID');
    }
    const workflowId = `sub-${runId}`;
    // Connect to Temporal Cloud using API key + TLS
    const connection = await client_1.Connection.connect({
        address,
        tls: true,
        apiKey,
    });
    const client = new client_1.Client({
        connection,
        namespace,
    });
    console.log(`Starting SubscriptionWorkflow with id: ${workflowId}`);
    // 1. Start the workflow; terminate any existing run with the same ID
    //    so we always get a fresh execution.
    const handle = await client.workflow.start(workflow_1.SubscriptionWorkflow, {
        taskQueue: 'sub-ts',
        workflowId,
        args: [{ userId: 'u1', tier: 'basic' }],
        workflowIdConflictPolicy: 'TERMINATE_EXISTING',
    });
    console.log(`Workflow started: ${workflowId}`);
    // 2. After 1 second, send upgrade signal
    await sleep(1000);
    await handle.signal(workflow_1.upgradeSignal, 'premium');
    console.log('Sent upgrade signal: premium');
    // 3. After another 2 seconds (~3s since start), query status
    await sleep(2000);
    const status = await handle.query(workflow_1.getStatusQuery);
    console.log('Status query result:', status);
    // 4. After another 2 seconds (~5s since start), send cancel signal
    await sleep(2000);
    await handle.signal(workflow_1.cancelSignal);
    console.log('Sent cancel signal');
    // 5. Await the final result
    const result = await handle.result();
    console.log(`Final result: ${JSON.stringify(result)}`);
}
main().catch((err) => {
    console.error('Client failed:', err);
    process.exit(1);
});
//# sourceMappingURL=client.js.map