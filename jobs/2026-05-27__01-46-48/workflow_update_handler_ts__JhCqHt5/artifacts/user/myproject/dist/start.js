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
const child_process_1 = require("child_process");
const path = __importStar(require("path"));
function startWorker() {
    const workerScript = path.join(__dirname, 'worker.js');
    const worker = (0, child_process_1.spawn)(process.execPath, [workerScript], {
        stdio: 'inherit',
        env: process.env,
    });
    worker.on('error', (err) => {
        console.error('Failed to start worker process:', err);
    });
    return worker;
}
async function runClient() {
    return new Promise((resolve, reject) => {
        const clientScript = path.join(__dirname, 'client.js');
        const client = (0, child_process_1.spawn)(process.execPath, [clientScript], {
            stdio: 'inherit',
            env: process.env,
        });
        client.on('error', reject);
        client.on('close', (code) => {
            if (code === 0) {
                resolve();
            }
            else {
                reject(new Error(`Client process exited with code ${code}`));
            }
        });
    });
}
async function main() {
    const workerProcess = startWorker();
    // Give the worker a moment to connect and start polling before the client runs
    await new Promise((resolve) => setTimeout(resolve, 3000));
    try {
        await runClient();
    }
    finally {
        // Shut down the worker once the client has finished
        workerProcess.kill('SIGTERM');
    }
}
main()
    .then(() => {
    process.exit(0);
})
    .catch((err) => {
    console.error('Error:', err);
    process.exit(1);
});
//# sourceMappingURL=start.js.map