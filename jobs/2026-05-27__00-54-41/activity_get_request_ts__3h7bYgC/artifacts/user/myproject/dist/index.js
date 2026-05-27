"use strict";
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
Object.defineProperty(exports, "__esModule", { value: true });
const worker_1 = require("@temporalio/worker");
const client_1 = require("@temporalio/client");
const workflows_1 = require("./workflows");
const activities = __importStar(require("./activities"));
async function run() {
    const address = process.env.TEMPORAL_ADDRESS;
    const namespace = process.env.TEMPORAL_NAMESPACE || 'default';
    const apiKey = process.env.TEMPORAL_API_KEY;
    const runId = process.env.ZEALT_RUN_ID || 'local';
    if (!address || !apiKey) {
        throw new Error("TEMPORAL_ADDRESS and TEMPORAL_API_KEY must be set");
    }
    const connectionOptions = {
        address,
        tls: true,
        apiKey,
    };
    // Worker Connection
    const workerConnection = await worker_1.NativeConnection.connect(connectionOptions);
    const worker = await worker_1.Worker.create({
        connection: workerConnection,
        namespace,
        taskQueue: 'fetch-url-ts',
        workflowsPath: require.resolve('./workflows'),
        activities,
    });
    const workerPromise = worker.run();
    // Client Connection
    const clientConnection = await client_1.Connection.connect(connectionOptions);
    const client = new client_1.Client({
        connection: clientConnection,
        namespace,
    });
    const workflowId = `fetch-wf-${runId}`;
    try {
        const handle = await client.workflow.start(workflows_1.FetchUrlWorkflow, {
            taskQueue: 'fetch-url-ts',
            workflowId,
            args: ['https://api.github.com/zen'],
        });
        const result = await handle.result();
        console.log(result);
    }
    finally {
        worker.shutdown();
        await workerPromise;
    }
}
run().catch((err) => {
    console.error(err);
    process.exit(1);
});
