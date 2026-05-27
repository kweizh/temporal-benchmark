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
const activities = __importStar(require("./activities"));
const TEMPORAL_ADDRESS = process.env.TEMPORAL_ADDRESS;
const TEMPORAL_API_KEY = process.env.TEMPORAL_API_KEY;
const TEMPORAL_NAMESPACE = process.env.TEMPORAL_NAMESPACE;
async function main() {
    const connection = await worker_1.NativeConnection.connect({
        address: TEMPORAL_ADDRESS,
        tls: true,
        apiKey: TEMPORAL_API_KEY,
        metadata: {
            'temporal-namespace': TEMPORAL_NAMESPACE,
        },
    });
    const worker = await worker_1.Worker.create({
        connection,
        namespace: TEMPORAL_NAMESPACE,
        taskQueue: 'progress-ts',
        workflowsPath: require.resolve('./workflow'),
        activities,
    });
    console.log('Worker started on task queue: progress-ts');
    await worker.run();
}
main().catch((err) => {
    console.error('Worker error:', err);
    process.exit(1);
});
