"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const worker_1 = require("@temporalio/worker");
async function run() {
    const address = process.env.TEMPORAL_ADDRESS;
    const namespace = process.env.TEMPORAL_NAMESPACE;
    const apiKey = process.env.TEMPORAL_API_KEY;
    if (!address || !namespace || !apiKey) {
        throw new Error('Missing required environment variables for Temporal Cloud connection');
    }
    const connection = await worker_1.NativeConnection.connect({
        address,
        apiKey,
        tls: true,
    });
    const worker = await worker_1.Worker.create({
        connection,
        namespace,
        taskQueue: 'counter-ts',
        workflowsPath: require.resolve('./workflows'),
    });
    console.log('Worker started');
    await worker.run();
}
run().catch((err) => {
    console.error(err);
    process.exit(1);
});
