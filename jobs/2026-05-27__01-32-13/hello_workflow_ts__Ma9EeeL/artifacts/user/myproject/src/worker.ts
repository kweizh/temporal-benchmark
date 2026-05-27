import { NativeConnection, Worker } from "@temporalio/worker";
import * as activities from "./activities";

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

  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue,
    workflowsPath: require.resolve("./workflows"),
    activities,
  });

  await worker.run();
}

run().catch((error) => {
  console.error("Worker failed:", error);
  process.exit(1);
});
