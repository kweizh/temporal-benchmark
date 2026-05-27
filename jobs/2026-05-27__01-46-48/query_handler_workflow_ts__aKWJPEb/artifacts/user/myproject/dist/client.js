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
const client_1 = require("@temporalio/client");
const workflow_1 = require("./workflow");
const fs = __importStar(require("fs"));
const TEMPORAL_ADDRESS = process.env.TEMPORAL_ADDRESS;
const TEMPORAL_API_KEY = process.env.TEMPORAL_API_KEY;
const TEMPORAL_NAMESPACE = process.env.TEMPORAL_NAMESPACE;
const ZEALT_RUN_ID = process.env.ZEALT_RUN_ID;
async function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
async function main() {
    const workflowId = `progress-${ZEALT_RUN_ID}`;
    const connection = await client_1.Connection.connect({
        address: TEMPORAL_ADDRESS,
        tls: true,
        apiKey: TEMPORAL_API_KEY,
        metadata: {
            'temporal-namespace': TEMPORAL_NAMESPACE,
        },
    });
    const client = new client_1.Client({
        connection,
        namespace: TEMPORAL_NAMESPACE,
    });
    console.log(`Starting workflow with id: ${workflowId}`);
    const handle = await client.workflow.start(workflow_1.ProgressWorkflow, {
        taskQueue: 'progress-ts',
        workflowId,
        args: [5],
    });
    console.log(`Workflow started. Waiting 2.5 seconds before querying...`);
    await sleep(2500);
    console.log('Sending getProgress query...');
    const progressResult = await handle.query(workflow_1.getProgressQuery);
    console.log('Query result:', progressResult);
    fs.writeFileSync('/workspace/progress.json', JSON.stringify(progressResult));
    console.log('Written progress.json:', progressResult);
    console.log('Awaiting final workflow result...');
    const finalResult = await handle.result();
    console.log('Final result:', finalResult);
}
main().catch((err) => {
    console.error('Client error:', err);
    process.exit(1);
});
