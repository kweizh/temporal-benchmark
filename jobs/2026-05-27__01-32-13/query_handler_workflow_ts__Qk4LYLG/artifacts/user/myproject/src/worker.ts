import { Connection } from "@temporalio/client";
import { Worker } from "@temporalio/worker";
import path from "path";
import * as activities from "./activities";

const taskQueue = "progress-ts";

async function runWorker(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;

  if (!address || !apiKey || !namespace) {
    throw new Error("Missing TEMPORAL_ADDRESS, TEMPORAL_API_KEY, or TEMPORAL_NAMESPACE env vars");
  }

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
    metadata: {
      "temporal-namespace": namespace,
    },
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue,
    workflowsPath: path.join(__dirname, "workflows"),
    activities,
  });

  await worker.run();
}

runWorker().catch((error) => {
  console.error(error);
  process.exit(1);
});
