/**
 * run.ts — Orchestrates the worker and client in a single Node process.
 *
 * Strategy:
 *   1. Start the Worker (non-blocking — it runs on its own async loop).
 *   2. Run the Client script which executes both workflows and waits for
 *      their terminal states.
 *   3. Shut the worker down gracefully.
 *   4. Exit with code 0.
 */
export {};
//# sourceMappingURL=run.d.ts.map