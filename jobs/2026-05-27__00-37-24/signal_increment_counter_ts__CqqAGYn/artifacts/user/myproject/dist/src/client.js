"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const client_1 = require("@temporalio/client");
const workflows_1 = require("./workflows");
async function run() {
    const address = process.env.TEMPORAL_ADDRESS;
    const namespace = process.env.TEMPORAL_NAMESPACE;
    const apiKey = process.env.TEMPORAL_API_KEY;
    const runId = process.env.ZEALT_RUN_ID;
    if (!address || !namespace || !apiKey || !runId) {
        throw new Error('Missing required environment variables');
    }
    const connection = await client_1.Connection.connect({
        address,
        apiKey,
        tls: true,
    });
    const client = new client_1.Client({
        connection,
        namespace,
    });
    const workflowId = `counter-wf-${runId}`;
    const handle = await client.workflow.start(workflows_1.CounterWorkflow, {
        taskQueue: 'counter-ts',
        workflowId,
    });
    console.log(`Started workflow ${workflowId}`);
    await handle.signal(workflows_1.incrementSignal, 5);
    await handle.signal(workflows_1.incrementSignal, 3);
    await handle.signal(workflows_1.incrementSignal, 2);
    await handle.signal(workflows_1.finishSignal);
    const result = await handle.result();
    console.log(result);
}
run().catch((err) => {
    console.error(err);
    process.exit(1);
});
