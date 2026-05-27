"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const worker_1 = require("@temporalio/worker");
const path_1 = __importDefault(require("path"));
async function run() {
    const apiKey = process.env.TEMPORAL_API_KEY;
    const address = process.env.TEMPORAL_ADDRESS;
    const namespace = process.env.TEMPORAL_NAMESPACE;
    if (!apiKey || !address || !namespace) {
        throw new Error('Missing required environment variables: TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE');
    }
    // Connect to Temporal Cloud using API key + TLS
    const connection = await worker_1.NativeConnection.connect({
        address,
        tls: true,
        apiKey,
    });
    const worker = await worker_1.Worker.create({
        connection,
        namespace,
        taskQueue: 'counter-ts',
        workflowsPath: path_1.default.resolve(__dirname, '../src/workflows.ts'),
        activities: {},
    });
    console.log('Worker started, polling task queue: counter-ts');
    await worker.run();
}
run().catch((err) => {
    console.error('Worker error:', err);
    process.exit(1);
});
