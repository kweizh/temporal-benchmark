"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const worker_1 = require("@temporalio/worker");
const path_1 = __importDefault(require("path"));
async function main() {
    const apiKey = process.env.TEMPORAL_API_KEY;
    const address = process.env.TEMPORAL_ADDRESS;
    const namespace = process.env.TEMPORAL_NAMESPACE;
    if (!apiKey)
        throw new Error('TEMPORAL_API_KEY environment variable is required');
    if (!address)
        throw new Error('TEMPORAL_ADDRESS environment variable is required');
    if (!namespace)
        throw new Error('TEMPORAL_NAMESPACE environment variable is required');
    const connection = await worker_1.NativeConnection.connect({
        address,
        tls: true,
        metadata: {
            'temporal-namespace': namespace,
        },
        apiKey,
    });
    const worker = await worker_1.Worker.create({
        connection,
        namespace,
        taskQueue: 'child-workflow-ts',
        // The Temporal bundler requires the TypeScript source path, not the compiled JS.
        // __dirname at runtime points to dist/, so we resolve back to src/.
        workflowsPath: path_1.default.resolve(__dirname, '..', 'src', 'workflows.ts'),
    });
    console.log('[Worker] Starting on task queue: child-workflow-ts');
    await worker.run();
}
main().catch((err) => {
    console.error('[Worker] Fatal error:', err);
    process.exit(1);
});
//# sourceMappingURL=worker.js.map