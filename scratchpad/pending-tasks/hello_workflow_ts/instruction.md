# Hello World Temporal Workflow (TypeScript)

## Background
You are building your first Temporal application using the Temporal.io TypeScript SDK. The goal is to connect to **Temporal Cloud** using an API key, run a Worker that hosts a simple Workflow and Activity, and use a Client to start the Workflow and print its result.

Temporal Cloud credentials are already provided to the environment as the following variables: `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE`. Do **NOT** hard-code or invent credentials; read them from the environment.

## Requirements
- Implement a TypeScript Temporal project that contains:
  - An **Activity** named `greet` that takes a string `name` and returns `Hello, <name>!`.
  - A **Workflow** named `HelloWorkflow` that accepts a string `name`, calls the `greet` activity, and returns its result.
  - A **Worker** that connects to Temporal Cloud (via API key + TLS) and polls the task queue `hello-world-ts`.
  - A **Client** entrypoint that connects to Temporal Cloud, starts (or executes) `HelloWorkflow` with the input `"Temporal"`, waits for completion, and prints the returned greeting to stdout.
- The Workflow ID must use the prefix `hello-wf-` and include the current `run-id` so concurrent runs do not collide (e.g. `hello-wf-${ZEALT_RUN_ID}`).
- The Worker and Client must use the task queue `hello-world-ts`.
- Provide an `npm start` script that runs the Worker in the background, runs the Client, waits for the workflow result, prints it, and then exits cleanly (the Worker may be terminated after the Client finishes).

## Implementation Hints
- Install the official TypeScript SDK packages: `@temporalio/client`, `@temporalio/worker`, `@temporalio/workflow`, `@temporalio/activity`.
- For the Client, use `Connection.connect` from `@temporalio/client` with `address`, `tls: true`, and `apiKey` options. For the Worker, use `NativeConnection.connect` from `@temporalio/worker` with the same connection options.
- Pass `namespace` to both the `Client` constructor and `Worker.create`.
- Read `ZEALT_RUN_ID`, `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE` from `process.env`.
- Use `proxyActivities` from `@temporalio/workflow` to invoke the activity from the workflow with a reasonable `startToCloseTimeout`.
- You can run the worker in the background of the same `npm start` script (for example with `concurrently`, a shell `&`, or by spawning it from the client script) — just make sure the workflow completes and its result is printed before the script exits.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: `npm start` (executed from `/home/user/myproject`)
- Task queue: `hello-world-ts`
- Workflow type name: `HelloWorkflow`
- Activity type name: `greet`
- Workflow ID: must start with `hello-wf-` and include the value of the `ZEALT_RUN_ID` environment variable
- When `npm start` is executed, the workflow `HelloWorkflow` must be started against Temporal Cloud using the namespace from `TEMPORAL_NAMESPACE`, run to completion, and the resulting greeting string returned from the activity must be printed to stdout.
- The completed workflow execution must be visible in Temporal Cloud (status `COMPLETED`) and its result must equal the greeting produced by the `greet` activity for the input `"Temporal"`.

