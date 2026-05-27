"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const client_1 = require("@temporalio/client");
const workflows_1 = require("./workflows");
async function main() {
    const apiKey = process.env.TEMPORAL_API_KEY;
    const address = process.env.TEMPORAL_ADDRESS;
    const namespace = process.env.TEMPORAL_NAMESPACE;
    const runId = process.env.ZEALT_RUN_ID ?? `local-${Date.now()}`;
    if (!apiKey)
        throw new Error('TEMPORAL_API_KEY environment variable is required');
    if (!address)
        throw new Error('TEMPORAL_ADDRESS environment variable is required');
    if (!namespace)
        throw new Error('TEMPORAL_NAMESPACE environment variable is required');
    const connection = await client_1.Connection.connect({
        address,
        tls: true,
        apiKey,
    });
    const client = new client_1.Client({
        connection,
        namespace,
    });
    const workflowId = `parent-wf-${runId}`;
    const input = [1, 2, 3];
    console.log(`[Client] Starting ParentSumWorkflow (id=${workflowId}) with input: [${input}]`);
    const result = await client.workflow.execute(workflows_1.ParentSumWorkflow, {
        taskQueue: 'child-workflow-ts',
        workflowId,
        args: [input],
    });
    console.log(result);
}
main().catch((err) => {
    console.error('[Client] Fatal error:', err);
    process.exit(1);
});
//# sourceMappingURL=client.js.map