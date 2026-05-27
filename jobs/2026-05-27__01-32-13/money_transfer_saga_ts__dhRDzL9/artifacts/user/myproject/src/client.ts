import { Client, Connection } from "@temporalio/client";
import type { MoneyTransferInput } from "./types";

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const runId = process.env.ZEALT_RUN_ID;

  if (!address || !apiKey || !namespace || !runId) {
    throw new Error("Missing required environment variables");
  }

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey
  });

  const client = new Client({
    connection,
    namespace
  });

  const successInput: MoneyTransferInput = {
    fromAccount: "A",
    toAccount: "B",
    amount: 30
  };

  const successHandle = await client.workflow.start("MoneyTransfer", {
    taskQueue: "saga-ts",
    workflowId: `saga-ok-${runId}`,
    args: [successInput]
  });

  await successHandle.result();
  console.log("Success workflow completed");

  const failureInput: MoneyTransferInput = {
    fromAccount: "A",
    toAccount: "B_FAIL",
    amount: 50
  };

  const failureHandle = await client.workflow.start("MoneyTransfer", {
    taskQueue: "saga-ts",
    workflowId: `saga-fail-${runId}`,
    args: [failureInput]
  });

  try {
    await failureHandle.result();
    console.log("Failure workflow unexpectedly completed");
  } catch (error) {
    console.log("Failure workflow failed as expected");
  }

  console.log("Workflows finished");
}

run().catch((error) => {
  console.error("Client failed", error);
  process.exit(1);
});
