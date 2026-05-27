import { NativeConnection, Worker } from "@temporalio/worker";
import { squareNumber } from "./activities";

const taskQueue = "parallel-squares-ts";

const {
  TEMPORAL_API_KEY: apiKey,
  TEMPORAL_ADDRESS: address,
  TEMPORAL_NAMESPACE: namespace,
} = process.env;

if (!apiKey || !address || !namespace) {
  throw new Error(
    "Missing TEMPORAL_API_KEY, TEMPORAL_ADDRESS, or TEMPORAL_NAMESPACE environment variables."
  );
}

async function run(): Promise<void> {
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
    activities: { squareNumber },
  });

  await worker.run();
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
