/**
 * Temporal Worker
 *
 * Connects to Temporal Cloud using API-key auth, registers
 * ParallelSquaresWorkflow and the squareNumber activity, then starts polling
 * the `parallel-squares-ts` task queue.
 *
 * Credentials are read exclusively from environment variables:
 *   TEMPORAL_API_KEY      – API key issued by Temporal Cloud
 *   TEMPORAL_ADDRESS      – <namespace>.tmprl.cloud:7233 (or similar)
 *   TEMPORAL_NAMESPACE    – Temporal Cloud namespace
 */
export {};
//# sourceMappingURL=worker.d.ts.map