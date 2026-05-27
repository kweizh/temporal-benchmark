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
async function main() {
    const workerScript = path.resolve(__dirname, 'worker.js');
    const clientScript = path.resolve(__dirname, 'client.js');
    // Start the worker in the background
    const workerProcess = (0, child_process_1.spawn)(process.execPath, [workerScript], {
        env: process.env,
        stdio: ['ignore', 'pipe', 'pipe'],
    });
    workerProcess.stdout?.on('data', (data) => {
        process.stdout.write(`[worker] ${data}`);
    });
    workerProcess.stderr?.on('data', (data) => {
        process.stderr.write(`[worker] ${data}`);
    });
    // Give the worker time to bundle workflows and connect (~15s for first bundle)
    await new Promise((resolve) => setTimeout(resolve, 15000));
    // Run the client
    const clientProcess = (0, child_process_1.spawn)(process.execPath, [clientScript], {
        env: process.env,
        stdio: ['ignore', 'pipe', 'pipe'],
    });
    clientProcess.stdout?.on('data', (data) => {
        process.stdout.write(data);
    });
    clientProcess.stderr?.on('data', (data) => {
        process.stderr.write(data);
    });
    // Wait for the client to finish
    const exitCode = await new Promise((resolve) => {
        clientProcess.on('close', (code) => {
            resolve(code ?? 0);
        });
    });
    // Kill the worker now that the client is done
    workerProcess.kill('SIGTERM');
    // Wait for worker to exit
    await new Promise((resolve) => {
        workerProcess.on('close', () => resolve());
        // Give it a few seconds to clean up, then force-resolve
        setTimeout(resolve, 5000);
    });
    process.exit(exitCode);
}
main().catch((err) => {
    console.error('Start script failed:', err);
    process.exit(1);
});
//# sourceMappingURL=start.js.map