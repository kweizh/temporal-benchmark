"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const child_process_1 = require("child_process");
async function main() {
    const worker = (0, child_process_1.spawn)('node', ['dist/src/worker.js'], {
        stdio: 'inherit',
        env: process.env,
    });
    // Give the worker some time to start
    await new Promise((resolve) => setTimeout(resolve, 5000));
    const client = (0, child_process_1.spawn)('node', ['dist/src/client.js'], {
        stdio: 'inherit',
        env: process.env,
    });
    client.on('exit', (code) => {
        worker.kill();
        process.exit(code || 0);
    });
    worker.on('error', (err) => {
        console.error('Worker error:', err);
        client.kill();
        process.exit(1);
    });
}
main().catch((err) => {
    console.error(err);
    process.exit(1);
});
