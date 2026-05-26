# Temporal Counter Workflow with Signals (TypeScript SDK)

## Background
Temporal Workflows can act like long-lived stateful services that receive asynchronous messages from clients. **Signals** mutate workflow state without returning a value, and `condition` lets a workflow block until some state predicate becomes true. In this task, you will use the Temporal **TypeScript SDK** with **Temporal Cloud** to build a counter workflow that accumulates values via an `increment` Signal and finishes when a `finish` Signal is received.

Temporal Cloud credentials are already provided to the environment as the following variables: `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE`. Do **NOT** hard-code or invent credentials; read them from the environment.

## Requirements
- Implement a TypeScript Temporal project that contains:
  - A **Workflow** named `CounterWorkflow` that:
    - Maintains an internal integer counter (initially `0`).
    - Defines a Signal `increment` (signal name `increment`) that takes a single `number` argument and adds it to the counter.
    - Defines a Signal `finish` (signal name `finish`) that sets an internal "done" flag.
    - Uses `condition` from `@temporalio/workflow` to wait until the done flag is set, then returns the final counter value (a `number`).
  - A **Worker** that connects to Temporal Cloud (via API key + TLS) and polls the task queue `counter-ts`, hosting `CounterWorkflow`.
  - A **Client** entrypoint that connects to Temporal Cloud, starts `CounterWorkflow` (workflow id prefix `counter-wf-` plus `ZEALT_RUN_ID`), sends a sequence of `increment` Signals with arguments `5`, `3`, and `2` (in order), then sends a `finish` Signal, awaits the workflow result, and prints the returned final counter value to stdout.
- The Workflow ID must use the prefix `counter-wf-` and include the current `run-id` so concurrent runs do not collide (e.g. `counter-wf-${ZEALT_RUN_ID}`).
- The Worker and Client must use the task queue `counter-ts`.
- Provide an `npm start` script that runs the Worker in the background, runs the Client, prints the final counter value, and then exits cleanly (the Worker may be terminated after the Client finishes).

## Implementation Hints
- Install the official TypeScript SDK packages: `@temporalio/client`, `@temporalio/worker`, `@temporalio/workflow`, `@temporalio/activity`.
- Define your Signal types statically using `defineSignal` from `@temporalio/workflow`, and register handlers with `setHandler` inside the workflow function.
- Use `condition(() => done)` to block until the `finish` Signal flips the flag, then return the counter.
- For the Client, use `Connection.connect` from `@temporalio/client` with `address`, `tls: true`, and `apiKey` options. For the Worker, use `NativeConnection.connect` from `@temporalio/worker` with the same options. Pass `namespace` to both the `Client` constructor and `Worker.create`.
- Read `ZEALT_RUN_ID`, `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE` from `process.env`.
- You can run the worker in the background of the same `npm start` script (for example with `concurrently`, a shell `&`, or by spawning it from the client script) — just make sure the workflow completes and its result is printed before the script exits.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: `npm start` (executed from `/home/user/myproject`)
- Task queue: `counter-ts`
- Workflow type name: `CounterWorkflow`
- Signal names: `increment` (single `number` argument) and `finish` (no arguments)
- Workflow ID: must start with `counter-wf-` and include the value of the `ZEALT_RUN_ID` environment variable
- When `npm start` is executed, the workflow `CounterWorkflow` must be started against Temporal Cloud using the namespace from `TEMPORAL_NAMESPACE`, receive a sequence of `increment` Signals followed by `finish`, run to completion, and the returned final counter value must be printed to stdout.
- The completed workflow execution must be visible in Temporal Cloud (status `COMPLETED`) and its result must equal the integer sum of the increments sent by the client.

