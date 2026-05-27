import { Client, Connection } from "@temporalio/client";
import { CounterWorkflow, finishSignal, incrementSignal } from "./workflows";

const taskQueue = "counter-ts";

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !apiKey || !namespace || !runId) {
    throw new Error(
      "Missing TEMPORAL_ADDRESS, TEMPORAL_API_KEY, TEMPORAL_NAMESPACE, or ZEALT_RUN_ID env vars."
    );
  }

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({
    connection,
    namespace,
  });

  const workflowId = `counter-wf-${runId}`;

  const handle = await client.workflow.start(CounterWorkflow, {
    taskQueue,
    workflowId,
  });

  await handle.signal(incrementSignal, 5);
  await handle.signal(incrementSignal, 3);
  await handle.signal(incrementSignal, 2);
  await handle.signal(finishSignal);

  const result = await handle.result();
  console.log(result);
}

run().catch((error) => {
  console.error("Client failed:", error);
  process.exit(1);
});
