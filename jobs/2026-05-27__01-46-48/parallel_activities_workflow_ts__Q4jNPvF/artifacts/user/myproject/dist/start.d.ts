/**
 * start.ts — Orchestrator for `npm start`
 *
 * 1. Spawns the compiled worker (dist/worker.js) as a background child process.
 * 2. Waits a moment for the worker to connect and begin polling.
 * 3. Runs the client inline: starts ParallelSquaresWorkflow, waits for the
 *    result, and prints it to stdout.
 * 4. Terminates the worker process and exits cleanly.
 */
export {};
//# sourceMappingURL=start.d.ts.map