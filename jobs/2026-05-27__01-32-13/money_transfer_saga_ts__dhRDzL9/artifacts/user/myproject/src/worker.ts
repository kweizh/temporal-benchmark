import { NativeConnection, Worker } from "@temporalio/worker";
import * as activities from "./activities";

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;

  if (!address || !apiKey || !namespace) {
    throw new Error("Missing Temporal Cloud environment variables");
  }

  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: "saga-ts",
    workflowsPath: require.resolve("./workflows"),
    activities
  });

  await worker.run();
}

run().catch((error) => {
  console.error("Worker failed", error);
  process.exit(1);
});
