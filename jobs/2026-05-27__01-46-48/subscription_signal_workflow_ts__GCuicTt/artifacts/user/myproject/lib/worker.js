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
const path = __importStar(require("path"));
async function main() {
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
        taskQueue: 'sub-ts',
        // workflowsPath must point to the TypeScript source so the Temporal
        // worker can bundle it with webpack into a deterministic sandbox.
        // We go up from lib/ to src/ at runtime.
        workflowsPath: path.resolve(__dirname, '..', 'src', 'workflow.ts'),
        activities,
    });
    console.log('Worker started, polling task queue: sub-ts');
    // Run until cancelled
    await worker.run();
}
main().catch((err) => {
    console.error('Worker failed:', err);
    process.exit(1);
});
//# sourceMappingURL=worker.js.map