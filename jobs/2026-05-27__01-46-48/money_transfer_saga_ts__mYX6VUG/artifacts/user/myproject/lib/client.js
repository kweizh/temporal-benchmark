"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const client_1 = require("@temporalio/client");
const workflows_1 = require("./workflows");
async function main() {
    const address = process.env.TEMPORAL_ADDRESS;
    const apiKey = process.env.TEMPORAL_API_KEY;
    const namespace = process.env.TEMPORAL_NAMESPACE;
    const runId = process.env.ZEALT_RUN_ID;
    if (!address || !apiKey || !namespace) {
        throw new Error('Missing required environment variables: TEMPORAL_ADDRESS, TEMPORAL_API_KEY, TEMPORAL_NAMESPACE');
    }
    if (!runId) {
        throw new Error('Missing required environment variable: ZEALT_RUN_ID');
    }
    console.log(`[client] Connecting to Temporal Cloud at ${address} (namespace: ${namespace})`);
    const connection = await client_1.Connection.connect({
        address,
        tls: true,
        apiKey,
    });
    const client = new client_1.Client({ connection, namespace });
    // -----------------------------------------------------------------------
    // Execution 1: Happy path — A → B, amount 30
    // -----------------------------------------------------------------------
    const okWorkflowId = `saga-ok-${runId}`;
    console.log(`\n[client] Starting workflow: ${okWorkflowId}`);
    const okHandle = await client.workflow.start(workflows_1.MoneyTransfer, {
        taskQueue: 'saga-ts',
        workflowId: okWorkflowId,
        args: [{ fromAccount: 'A', toAccount: 'B', amount: 30 }],
    });
    console.log(`[client] Waiting for ${okWorkflowId} to complete...`);
    await okHandle.result();
    console.log(`[client] ✅ ${okWorkflowId} — COMPLETED`);
    // -----------------------------------------------------------------------
    // Execution 2: Failure path — A → B_FAIL, amount 50 (deposit will fail)
    // -----------------------------------------------------------------------
    const failWorkflowId = `saga-fail-${runId}`;
    console.log(`\n[client] Starting workflow: ${failWorkflowId}`);
    const failHandle = await client.workflow.start(workflows_1.MoneyTransfer, {
        taskQueue: 'saga-ts',
        workflowId: failWorkflowId,
        args: [{ fromAccount: 'A', toAccount: 'B_FAIL', amount: 50 }],
    });
    console.log(`[client] Waiting for ${failWorkflowId} to reach terminal state...`);
    try {
        await failHandle.result();
        // If we somehow reach here, it means the workflow completed — that's unexpected.
        console.warn(`[client] ⚠️  ${failWorkflowId} completed unexpectedly (expected FAILED)`);
    }
    catch (err) {
        if (err instanceof client_1.WorkflowFailedError) {
            console.log(`[client] ✅ ${failWorkflowId} — FAILED as expected (compensation applied)`);
            console.log(`[client]    Failure reason: ${err.cause?.message ?? err.message}`);
        }
        else {
            // Unexpected error type — rethrow so the process exits non-zero
            throw err;
        }
    }
    // -----------------------------------------------------------------------
    // Summary
    // -----------------------------------------------------------------------
    const fs = await import('fs');
    const accounts = JSON.parse(fs.readFileSync('/workspace/accounts.json', 'utf8'));
    console.log('\n[client] ─── Final account balances ───────────────────────────────');
    console.log(`[client]   ${JSON.stringify(accounts, null, 2)}`);
    console.log('[client] ───────────────────────────────────────────────────────────');
    console.log('[client] Done. Exiting cleanly.');
    await connection.close();
}
main().catch((err) => {
    console.error('[client] Fatal error:', err);
    process.exit(1);
});
//# sourceMappingURL=client.js.map