# Temporal Counter Workflow with Signals and Queries (Python SDK)

## Background
Temporal Workflows can act like long-lived stateful services that receive messages from clients. **Signals** mutate workflow state asynchronously, and **Queries** read workflow state synchronously without affecting history. In this task, you will use the Temporal **Python SDK** with **Temporal Cloud** to build a counter workflow that accumulates values via Signals, exposes its state through a Query, and finishes when a `finish` Signal is received.

## Requirements
- Implement a Temporal Workflow named `CounterWorkflow` in Python that:
  - Maintains an integer counter (initially `0`).
  - Exposes a Signal handler `increment(n: int)` that adds `n` to the counter.
  - Exposes a Signal handler `finish()` that releases the workflow's main wait so it can complete.
  - Exposes a Query handler `get_count()` that returns the current counter value (an `int`).
  - The workflow's main `run` method must wait until `finish` has been received, then return the final counter value (an `int`).
- Implement a Worker that polls the task queue `counter-py` and hosts `CounterWorkflow`.
- Implement a Client script that:
  1. Starts the `CounterWorkflow` (workflow id `counter-${ZEALT_RUN_ID}`, task queue `counter-py`).
  2. Sends three `increment` Signals with arguments `1`, `2`, and `3` (in order).
  3. Sends a `get_count` Query and prints the returned value.
  4. Sends a `finish` Signal.
  5. Waits for the workflow result and writes a line in the form `final=<n>` to `/workspace/counter.out` (e.g. `final=6`).
- Connect to **Temporal Cloud** using the environment variables `TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`, and `TEMPORAL_API_KEY`. Do **not** mock Temporal.

## Implementation Hints
- Install the `temporalio` Python SDK.
- Use `temporalio.client.Client.connect(...)` with the API key, address, and namespace from environment variables. Temporal Cloud requires TLS; pass `tls=True` when using an API key.
- Decorate workflow methods with `@workflow.defn`, `@workflow.run`, `@workflow.signal`, and `@workflow.query`.
- Use `workflow.wait_condition(lambda: ...)` to block the main `run` method until the `finish` signal sets a flag.
- The Worker must be running while the client sends signals/queries and awaits the result. Run the worker as a separate process (or background task) on the task queue `counter-py`.
- Read the `ZEALT_RUN_ID` environment variable to scope the workflow id (`counter-${ZEALT_RUN_ID}`) so multiple runs don't collide.

## Acceptance Criteria
- Project path: `/home/user/counter-py`
- Task queue: `counter-py`
- Workflow id: `counter-${ZEALT_RUN_ID}` where `ZEALT_RUN_ID` is read from the environment.
- Workflow type name: `CounterWorkflow`
- Output file: `/workspace/counter.out` — must contain a line `final=6` after the client completes.
- The workflow execution must reach status `COMPLETED` on Temporal Cloud, with a numeric result of `6`.
- The client must use the real Temporal Cloud connection (`TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`, `TEMPORAL_API_KEY`). Mocking the Temporal client or server is not allowed.

