"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.runClient = runClient;
const client_1 = require("@temporalio/client");
const workflows_1 = require("./workflows");
async function runClient() {
    const apiKey = process.env.TEMPORAL_API_KEY;
    const address = process.env.TEMPORAL_ADDRESS;
    const namespace = process.env.TEMPORAL_NAMESPACE;
    const runId = process.env.ZEALT_RUN_ID ?? 'local';
    if (!apiKey || !address || !namespace) {
        throw new Error('Missing required environment variables: TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE');
    }
    const connection = await client_1.Connection.connect({
        address,
        tls: true,
        apiKey,
    });
    const client = new client_1.Client({
        connection,
        namespace,
    });
    const workflowId = `hello-wf-${runId}`;
    console.log(`Starting HelloWorkflow with ID: ${workflowId}`);
    const result = await client.workflow.execute(workflows_1.HelloWorkflow, {
        taskQueue: 'hello-world-ts',
        workflowId,
        args: ['Temporal'],
    });
    console.log(result);
    await connection.close();
}
// Allow direct execution: `node dist/client.js`
if (require.main === module) {
    runClient().catch((err) => {
        console.error('Client failed:', err);
        process.exit(1);
    });
}
//# sourceMappingURL=client.js.map