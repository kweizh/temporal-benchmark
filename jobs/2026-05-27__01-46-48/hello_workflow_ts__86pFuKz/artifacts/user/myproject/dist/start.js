"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const child_process_1 = require("child_process");
const path_1 = __importDefault(require("path"));
const client_1 = require("./client");
async function main() {
    // Spawn the worker as a background child process
    const workerProcess = (0, child_process_1.spawn)(process.execPath, [path_1.default.join(__dirname, 'worker.js')], {
        env: process.env,
        stdio: ['ignore', 'pipe', 'pipe'],
        detached: false,
    });
    workerProcess.stdout?.on('data', (data) => {
        process.stdout.write(`[worker] ${data}`);
    });
    workerProcess.stderr?.on('data', (data) => {
        process.stderr.write(`[worker] ${data}`);
    });
    workerProcess.on('error', (err) => {
        console.error('Worker process error:', err);
    });
    // Give the worker time to connect and start polling before the client fires
    await new Promise((resolve) => setTimeout(resolve, 4000));
    try {
        await (0, client_1.runClient)();
    }
    finally {
        // Terminate the background worker cleanly after the workflow completes
        workerProcess.kill('SIGTERM');
        // Brief pause to allow process cleanup
        await new Promise((resolve) => setTimeout(resolve, 500));
    }
    process.exit(0);
}
main().catch((err) => {
    console.error('Fatal error in start script:', err);
    process.exit(1);
});
//# sourceMappingURL=start.js.map