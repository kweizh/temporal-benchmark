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
/**
 * start.ts — orchestrates Worker (background child process) + Client (in-process).
 *
 * 1. Spawns the worker as a child process.
 * 2. Waits for the worker to connect and start polling.
 * 3. Runs the client logic in-process to start the workflow and await its result.
 * 4. Prints the result, then kills the worker child process and exits.
 */
const child_process_1 = require("child_process");
const path = __importStar(require("path"));
const client_main_1 = require("./client-main");
function delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
async function run() {
    const workerScript = path.join(__dirname, 'worker.js');
    // Spawn worker as a separate OS process so it can run concurrently
    const workerProcess = (0, child_process_1.spawn)(process.execPath, [workerScript], {
        stdio: 'inherit',
        env: process.env,
    });
    workerProcess.on('error', (err) => {
        console.error('Worker process error:', err);
    });
    // Give the worker time to establish the Temporal Cloud connection and begin polling
    await delay(4000);
    try {
        // Run the client: starts the workflow, waits for result, prints it
        await (0, client_main_1.main)();
    }
    finally {
        // Cleanly shut down the worker child process
        workerProcess.kill('SIGTERM');
    }
}
run().catch((err) => {
    console.error(err);
    process.exit(1);
});
//# sourceMappingURL=start.js.map