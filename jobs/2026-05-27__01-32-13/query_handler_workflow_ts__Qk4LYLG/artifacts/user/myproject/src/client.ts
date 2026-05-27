import { Connection, Client } from "@temporalio/client";
import { promises as fs } from "fs";

const taskQueue = "progress-ts";

async function runClient(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !apiKey || !namespace) {
    throw new Error("Missing TEMPORAL_ADDRESS, TEMPORAL_API_KEY, or TEMPORAL_NAMESPACE env vars");
  }
  if (!runId) {
    throw new Error("Missing ZEALT_RUN_ID env var");
  }

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
    metadata: {
      "temporal-namespace": namespace,
    },
  });

  const client = new Client({
    connection,
    namespace,
  });

  await fs.writeFile("/workspace/progress.log", "");

  const workflowId = `progress-${runId}`;
  const handle = await client.workflow.start("ProgressWorkflow", {
    workflowId,
    taskQueue,
    args: [5],
  });

  await new Promise((resolve) => {
    setTimeout(resolve, 2500);
  });

  const progress = await handle.query("getProgress");
  await fs.writeFile("/workspace/progress.json", JSON.stringify(progress, null, 2));

  await handle.result();
}

runClient().catch((error) => {
  console.error(error);
  process.exit(1);
});
