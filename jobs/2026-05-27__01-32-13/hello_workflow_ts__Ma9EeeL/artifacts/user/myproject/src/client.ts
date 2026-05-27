import { Connection, Client } from "@temporalio/client";
import { HelloWorkflow } from "./workflows";

const taskQueue = "hello-world-ts";

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

async function run(): Promise<void> {
  const address = requireEnv("TEMPORAL_ADDRESS");
  const namespace = requireEnv("TEMPORAL_NAMESPACE");
  const apiKey = requireEnv("TEMPORAL_API_KEY");
  const runId = requireEnv("ZEALT_RUN_ID");

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({ connection, namespace });

  const result = await client.workflow.execute(HelloWorkflow, {
    taskQueue,
    workflowId: `hello-wf-${runId}`,
    args: ["Temporal"],
  });

  console.log(result);
}

run().catch((error) => {
  console.error("Client failed:", error);
  process.exit(1);
});
