# Parent/Child Workflow with `executeChild` (TypeScript)

## Background
You are extending a Temporal.io TypeScript project that already connects to **Temporal Cloud** via an API key. The goal is to demonstrate the *Child Workflow* pattern: a parent Workflow that orchestrates one or more child Workflow executions and aggregates their results.

Temporal Cloud credentials are already provided to the environment as the following variables: `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE`. Do **NOT** hard-code or invent credentials; read them from the environment.

## Requirements
- Implement a TypeScript Temporal project that contains:
  - A **Child Workflow** named `DoubleWorkflow` that accepts a single `number` argument `n` and returns `n * 2`.
  - A **Parent Workflow** named `ParentSumWorkflow` that accepts an array of numbers and:
    - Invokes `DoubleWorkflow` once per element using the `executeChild` Child Workflow API (no Activities).
    - Returns the sum of all doubled values.
  - A **Worker** that registers **both** workflows on the same task queue (`child-workflow-ts`) and connects to Temporal Cloud (TLS + API key).
  - A **Client** entrypoint that connects to Temporal Cloud, starts (or executes) `ParentSumWorkflow` with the input `[1, 2, 3]`, waits for completion, and prints the numeric result to stdout.
- The Workflow ID of the parent execution must use the prefix `parent-wf-` and include the current `run-id` (e.g. `parent-wf-${ZEALT_RUN_ID}`) so concurrent runs do not collide.
- The Worker and Client must use the task queue `child-workflow-ts`.
- Provide an `npm start` script that runs the Worker in the background, runs the Client, waits for the parent workflow result, prints it, and then exits cleanly (the Worker may be terminated after the Client finishes).

## Implementation Hints
- Install the official TypeScript SDK packages: `@temporalio/client`, `@temporalio/worker`, `@temporalio/workflow`.
- Use `executeChild` from `@temporalio/workflow` inside the parent workflow to start child workflow executions and await their results.
- Register both workflows by pointing `Worker.create({ workflowsPath: ... })` at the file/module that exports them.
- For the Client, use `Connection.connect` from `@temporalio/client` with `address`, `tls: true`, and `apiKey` options. For the Worker, use `NativeConnection.connect` from `@temporalio/worker` with the same connection options.
- Pass `namespace` to both the `Client` constructor and `Worker.create`.
- Read `ZEALT_RUN_ID`, `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE` from `process.env`.
- You can run the worker in the background of the same `npm start` script (for example with `concurrently`, a shell `&`, or by spawning it from the client script) — just make sure the parent workflow completes and its result is printed before the script exits.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: `npm start` (executed from `/home/user/myproject`)
- Task queue: `child-workflow-ts`
- Parent Workflow type name: `ParentSumWorkflow`
- Child Workflow type name: `DoubleWorkflow`
- Parent Workflow ID: must start with `parent-wf-` and include the value of the `ZEALT_RUN_ID` environment variable
- When `npm start` is executed, `ParentSumWorkflow` must be started against Temporal Cloud using the namespace from `TEMPORAL_NAMESPACE`, run to completion, and the numeric sum returned by the parent workflow must be printed to stdout.
- The completed parent workflow execution must be visible in Temporal Cloud (status `COMPLETED`) and its result must equal the sum of `n * 2` for each `n` in the client input array.
- At least one `DoubleWorkflow` execution started as a child of the parent must be visible in Temporal Cloud in the same time window.

