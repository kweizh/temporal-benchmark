# Evaluation Dataset Research: Temporal.io
## 1. Library Overview
*   **Description**: Temporal.io is a durable execution platform that enables developers to build scalable, reliable applications by orchestrating complex workflows. It ensures that code is executed reliably even in the face of network failures, server crashes, or long-running processes (months or years).
*   **Ecosystem Role**: Temporal acts as a "durable state machine" in the backend. It sits between your services, managing retries, state persistence, and execution flow, replacing ad-hoc cron jobs, message queues, and manual state management.
*   **Project Setup**:
    *   **TypeScript**:
        ```bash
        npm install @temporalio/client @temporalio/worker @temporalio/workflow @temporalio/activity
        # For environment config support
        npm install @temporalio/envconfig
        ```
    *   **Python**:
        ```bash
        pip install temporalio
        ```
    *   **Temporal Cloud Configuration**:
        To connect to Temporal Cloud, set the following environment variables:
        ```bash
        export TEMPORAL_API_KEY="your_api_key"
        export TEMPORAL_ADDRESS="your-namespace.account-id.tmprl.cloud:7233"
        export TEMPORAL_NAMESPACE="your-namespace.account-id"
        ```
## 2. Core Primitives & APIs
*   **Workflow**: A durable function that orchestrates activities. Must be deterministic.
    *   [Documentation](https://docs.temporal.io/develop/typescript/workflows/basics)
*   **Activity**: A function for non-deterministic operations (API calls, DB access).
    *   [Documentation](https://docs.temporal.io/develop/typescript/activities)
*   **Worker**: The process that hosts and executes Workflow and Activity code.
    *   [Documentation](https://docs.temporal.io/develop/typescript/workers)
*   **Client**: Used to start, signal, query, and describe Workflows.
    *   [Documentation](https://docs.temporal.io/develop/typescript/client/temporal-client)

### Consistency Guarantees
There are 2 categories of APIs from the Temporal backend: one with a guarantee of strong consistency, and one without.
*   The `describe` API (used in the UI) is backed by APIs which guarantee strong consistency. This same group of APIs is also used during workflow execution.
*   The `list` API (used in the UI) is backed by APIs which only guarantee eventual consistency.
*   When a status needs to be checked, you should use the `describe` API of Temporal to get the latest status.

### Code Snippet: TypeScript Cloud Connection

```typescript
import { Connection, Client } from '@temporalio/client';
import { loadClientConnectConfig } from '@temporalio/envconfig';
async function run() {
  // Automatically loads TEMPORAL_API_KEY, TEMPORAL_ADDRESS, etc.
  const config = loadClientConnectConfig();

  const connection = await Connection.connect(config.connectionOptions);
  const client = new Client({
    connection,
    namespace: config.namespace
  });
  const handle = await client.workflow.start('MyWorkflow', {
    taskQueue: 'my-task-queue',
    workflowId: 'wf-id-123',
    args: [{ data: 'hello' }]
  });

  console.log(`Started workflow ${handle.workflowId}`);
}
```

In typescript, there may be types when using the SDK, for example:

```typescript
while (counter < target) {
  counter = await incrementCounter(counter);
  iterations++;

  if (iterations >= 10 && counter < target) {
    await continueAsNew<typeof LongLoopWorkflow>(counter, target);
  }
}
```

### Code Snippet: Python Cloud Connection

```python
import os
import asyncio
from temporalio.client import Client
async def main():
    # Manual connection using environment variables
    client = await Client.connect(
        os.getenv("TEMPORAL_ADDRESS"),
        namespace=os.getenv("TEMPORAL_NAMESPACE"),
        api_key=os.getenv("TEMPORAL_API_KEY")
    )

    result = await client.execute_workflow(
        "MyWorkflow",
        "arg1",
        id="wf-id-123",
        task_queue="my-task-queue"
    )
    print(f"Result: {result}")
if __name__ == "__main__":
    asyncio.run(main())
```

Please note that the timestamp in protobuf needs to be handled carefully, the `ToMicroseconds()` method converts the timestamp to microseconds.
If any timestamp is needed, it should be handled like:

```python
epoch_seconds = [t.ToMicroseconds() / 1e6 for t in scheduled_times]
```

## 3. Real-World Use Cases & Templates
*   **Subscription Management**: Handling recurring billing, trial periods, and cancellation logic over months.
    *   [TS Template](https://github.com/temporalio/subscription-workflow-project-template-typescript)
*   **Saga Pattern (E-commerce)**: Coordinating multi-step transactions (Reserve stock -> Charge card -> Ship) with "compensation" steps if one fails.
    *   [Saga Example](https://github.com/temporalio/samples-typescript/tree/main/saga)
*   **Infrastructure Provisioning**: Orchestrating cloud resource creation (VPC -> Subnet -> EC2) with long waits and retries.
*   **Integration Patterns**: Using Activities to wrap flaky 3rd-party APIs (Stripe, Twilio) with exponential backoff.
## 4. Developer Friction Points
*   **Non-Determinism**: Using `Date.now()`, `Math.random()`, or making network calls directly inside a Workflow function. This causes "Non-deterministic error" during replay.
    *   *Task*: Fix a workflow that uses `new Date()` to determine a discount.
*   **Task Queue Mismatch**: The Client starts a workflow on `queue-A`, but the Worker is polling `queue-B`. The workflow stays in "Running" state forever with no progress.
    *   *Task*: Debug why a started workflow isn't executing.
*   **Large History / Continue-As-New**: Workflows that run forever (e.g., a "User Wallet" workflow) accumulate too many events. Developers must use `continueAsNew` to reset history.
    *   *Task*: Refactor a long-running loop to use `continueAsNew` after 100 iterations.
*   **mTLS vs API Key**: Misconfiguring TLS when connecting to Cloud. Using the wrong endpoint format (mTLS vs API Key endpoints differ slightly).
## 5. Evaluation Ideas
*   **Simple**: Connect to Temporal Cloud using `TEMPORAL_API_KEY` and trigger a "Hello World" workflow.
*   **Simple**: Implement a basic Activity that performs a GET request to a mock API and returns the result.
*   **Intermediate**: Create a "Reminder" workflow that sleeps for a user-provided duration and then calls a "Notify" activity.
*   **Intermediate**: Implement a Workflow that retries a failing Activity exactly 5 times with a 2-second fixed delay.
*   **Complex**: Build a "Money Transfer" Saga that withdraws from Account A and deposits to Account B, with a compensation step to refund Account A if Deposit B fails.
*   **Complex**: Implement a "Subscription" workflow that handles a 30-day billing cycle and uses `Signals` to allow users to "Upgrade" or "Cancel" mid-cycle.
*   **Edge Case**: Debug and fix a "Non-deterministic" error in a provided workflow that uses global variables or system time for logic.
*   **Edge Case**: Migrate a long-running workflow's state to a new version using the `patch` (TS) or `patched` (Python) versioning API.
## 6. Sources
1.  [Temporal Cloud API Keys](https://docs.temporal.io/cloud/api-keys) - Official guide on creating and using API keys.
2.  [Temporal Client Environment Configuration](https://docs.temporal.io/develop/environment-configuration) - Details on `TEMPORAL_API_KEY` and TOML profiles.
3.  [TypeScript SDK Client Docs](https://docs.temporal.io/develop/typescript/client/temporal-client) - Connection and workflow execution patterns for TS.
4.  [Python SDK Client Docs](https://docs.temporal.io/develop/python/client/temporal-client) - Connection and workflow execution patterns for Python.
5.  [Workflow Determinism Constraints](https://docs.temporal.io/develop/typescript/workflows/basics#deterministic-constraints) - Explanation of what code is allowed inside workflows.
6.  [Temporal Samples (GitHub)](https://github.com/temporalio/samples-typescript) - Collection of real-world implementation patterns.