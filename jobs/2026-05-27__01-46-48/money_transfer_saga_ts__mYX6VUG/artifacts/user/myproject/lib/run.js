"use strict";
/**
 * run.ts — Orchestrates the worker and client in a single Node process.
 *
 * Strategy:
 *   1. Start the Worker (non-blocking — it runs on its own async loop).
 *   2. Run the Client script which executes both workflows and waits for
 *      their terminal states.
 *   3. Shut the worker down gracefully.
 *   4. Exit with code 0.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const worker_1 = require("@temporalio/worker");
const client_1 = require("@temporalio/client");
const activities = __importStar(require("./activities"));
const workflows_1 = require("./workflows");
const path_1 = __importDefault(require("path"));
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
    // -----------------------------------------------------------------------
    // 1. Start the Worker
    // -----------------------------------------------------------------------
    console.log(`[run] Connecting worker to Temporal Cloud at ${address} (namespace: ${namespace})`);
    const workerConnection = await worker_1.NativeConnection.connect({
        address,
        tls: true,
        apiKey,
    });
    const worker = await worker_1.Worker.create({
        connection: workerConnection,
        namespace,
        taskQueue: 'saga-ts',
        workflowsPath: path_1.default.resolve(__dirname, 'workflows'),
        activities,
    });
    console.log('[run] Worker created, starting poll loop...');
    // Run the worker in the background — do NOT await here.
    const workerRunPromise = worker.run();
    // Give the worker a moment to register itself before sending work.
    await new Promise((resolve) => setTimeout(resolve, 1500));
    // -----------------------------------------------------------------------
    // 2. Connect the Client
    // -----------------------------------------------------------------------
    console.log('[run] Connecting client...');
    const clientConnection = await client_1.Connection.connect({
        address,
        tls: true,
        apiKey,
    });
    const client = new client_1.Client({ connection: clientConnection, namespace });
    // -----------------------------------------------------------------------
    // 3. Workflow 1 — Happy path: A → B, amount 30
    // -----------------------------------------------------------------------
    const okWorkflowId = `saga-ok-${runId}`;
    console.log(`\n[run] Starting workflow: ${okWorkflowId}`);
    const okHandle = await client.workflow.start(workflows_1.MoneyTransfer, {
        taskQueue: 'saga-ts',
        workflowId: okWorkflowId,
        args: [{ fromAccount: 'A', toAccount: 'B', amount: 30 }],
    });
    console.log(`[run] Waiting for ${okWorkflowId} to complete...`);
    await okHandle.result();
    console.log(`[run] ✅ ${okWorkflowId} reached COMPLETED`);
    // -----------------------------------------------------------------------
    // 4. Workflow 2 — Failure path: A → B_FAIL, amount 50
    // -----------------------------------------------------------------------
    const failWorkflowId = `saga-fail-${runId}`;
    console.log(`\n[run] Starting workflow: ${failWorkflowId}`);
    const failHandle = await client.workflow.start(workflows_1.MoneyTransfer, {
        taskQueue: 'saga-ts',
        workflowId: failWorkflowId,
        args: [{ fromAccount: 'A', toAccount: 'B_FAIL', amount: 50 }],
    });
    console.log(`[run] Waiting for ${failWorkflowId} to reach terminal state...`);
    try {
        await failHandle.result();
        console.warn(`[run] ⚠️  ${failWorkflowId} completed unexpectedly (expected FAILED)`);
    }
    catch (err) {
        if (err instanceof client_1.WorkflowFailedError) {
            console.log(`[run] ✅ ${failWorkflowId} reached FAILED as expected (compensation applied)`);
            console.log(`[run]    Cause: ${err.cause?.message ?? err.message}`);
        }
        else {
            throw err;
        }
    }
    // -----------------------------------------------------------------------
    // 5. Summary
    // -----------------------------------------------------------------------
    const fs = await import('fs');
    const accounts = JSON.parse(fs.readFileSync('/workspace/accounts.json', 'utf8'));
    console.log('\n[run] ─── Final account balances ───────────────────────────────');
    console.log(JSON.stringify(accounts, null, 2));
    console.log('[run] ────────────────────────────────────────────────────────────');
    // -----------------------------------------------------------------------
    // 6. Shut down the worker and exit
    // -----------------------------------------------------------------------
    console.log('[run] Shutting down worker...');
    worker.shutdown();
    await workerRunPromise;
    await clientConnection.close();
    console.log('[run] All done. Exiting with code 0.');
}
main().catch((err) => {
    console.error('[run] Fatal error:', err);
    process.exit(1);
});
//# sourceMappingURL=run.js.map