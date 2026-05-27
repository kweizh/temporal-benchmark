"use strict";
/**
 * start.ts — Orchestrator for `npm start`
 *
 * 1. Spawns the compiled worker (dist/worker.js) as a background child process.
 * 2. Waits a moment for the worker to connect and begin polling.
 * 3. Runs the client inline: starts ParallelSquaresWorkflow, waits for the
 *    result, and prints it to stdout.
 * 4. Terminates the worker process and exits cleanly.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const child_process_1 = require("child_process");
const client_1 = require("@temporalio/client");
const workflows_1 = require("./workflows");
const path_1 = __importDefault(require("path"));
const TASK_QUEUE = 'parallel-squares-ts';
const INPUT = [1, 2, 3, 4, 5];
// ── helpers ────────────────────────────────────────────────────────────────
function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
function startWorker() {
    const workerPath = path_1.default.resolve(__dirname, 'worker.js');
    const proc = (0, child_process_1.spawn)(process.execPath, [workerPath], {
        stdio: 'inherit',
        env: process.env,
    });
    proc.on('error', (err) => {
        console.error('[start] Worker process error:', err);
    });
    return proc;
}
// ── main ───────────────────────────────────────────────────────────────────
async function main() {
    const apiKey = process.env.TEMPORAL_API_KEY;
    const address = process.env.TEMPORAL_ADDRESS;
    const namespace = process.env.TEMPORAL_NAMESPACE;
    const runId = process.env.ZEALT_RUN_ID;
    if (!apiKey || !address || !namespace || !runId) {
        throw new Error('Missing required environment variables: TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, ZEALT_RUN_ID');
    }
    const workflowId = `parallel-wf-${runId}`;
    // 1. Launch worker in the background.
    console.log('[start] Launching worker …');
    const workerProc = startWorker();
    // 2. Give the worker time to connect and start polling before submitting work.
    await sleep(5000);
    // 3. Connect the client and execute the workflow.
    const connection = await client_1.Connection.connect({
        address,
        tls: true,
        apiKey,
    });
    const client = new client_1.Client({ connection, namespace });
    console.log(`[start] Starting workflow "${workflowId}" with input: [${INPUT.join(', ')}]`);
    let result;
    try {
        result = await client.workflow.execute(workflows_1.ParallelSquaresWorkflow, {
            taskQueue: TASK_QUEUE,
            workflowId,
            args: [INPUT],
        });
    }
    finally {
        // 4. Always clean up the worker regardless of workflow success/failure.
        console.log('[start] Workflow finished. Shutting down worker …');
        workerProc.kill('SIGTERM');
        await connection.close();
    }
    // Print the final result — this is what the acceptance criteria check.
    console.log(`${result}`);
}
main().catch((err) => {
    console.error('[start] Fatal error:', err);
    process.exit(1);
});
//# sourceMappingURL=start.js.map