import { Client, Connection } from "@temporalio/client";
import { ParallelSquaresWorkflow } from "./workflows";

const taskQueue = "parallel-squares-ts";

const {
  TEMPORAL_API_KEY: apiKey,
  TEMPORAL_ADDRESS: address,
  TEMPORAL_NAMESPACE: namespace,
  ZEALT_RUN_ID: runId,
} = process.env;

if (!apiKey || !address || !namespace || !runId) {
  throw new Error(
    "Missing TEMPORAL_API_KEY, TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, or ZEALT_RUN_ID environment variables."
  );
}

async function run(): Promise<void> {
  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({
    connection,
    namespace,
  });

  const numbers = [1, 2, 3, 4, 5];

  const result = await client.workflow.execute(ParallelSquaresWorkflow, {
    taskQueue,
    workflowId: `parallel-wf-${runId}`,
    args: [numbers],
  });

  console.log(result);
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
