# Long-Running Workflow with Continue-As-New (Python SDK)

## Background
Long-running Temporal Workflows can accumulate large Event Histories. To keep history bounded, the Temporal Python SDK exposes `workflow.continue_as_new(...)`, which atomically completes the current Workflow run and starts a fresh run (with a new Run ID but the same Workflow ID), forwarding any state needed to resume work. In this task, you will use the Temporal **Python SDK** with **Temporal Cloud** to build a workflow that performs a long incrementing loop, checkpointing itself by calling `continue_as_new` every 10 iterations until it reaches a target.

## Requirements
- Implement an Activity `increment_counter` in Python that:
  - Accepts a single `int` argument (the next value to record).
  - Appends a single line `<value>\n` (decimal representation followed by a newline) to the file `/workspace/loop.log`.
  - Returns the value it just recorded.
- Implement a Temporal Workflow named `LongLoopWorkflow` in Python that:
  - Takes two `int` arguments: `start` and `target`.
  - Executes the `increment_counter` Activity in a loop, beginning with `start + 1` and increasing by `1` each iteration, until the recorded value equals `target`.
  - Performs at most **10 activity invocations per Workflow run**. As soon as 10 activities have completed in the current run, the Workflow must call `workflow.continue_as_new(...)` to start a new run with `start` updated to the last recorded value and `target` unchanged.
  - Returns `target` (an `int`) from the final run, once the recorded value reaches `target`.
- Implement a Worker that polls the task queue `loop-py` and hosts both `LongLoopWorkflow` and `increment_counter`.
- Implement a Client script that:
  1. Connects to Temporal Cloud.
  2. Starts (or executes) the `LongLoopWorkflow` with arguments `start=0`, `target=25`, using workflow id `loop-py-${ZEALT_RUN_ID}` and task queue `loop-py`.
  3. Awaits the final result and writes the line `result=<n>` (e.g. `result=25`) to `/workspace/loop.out`.
- Connect to **Temporal Cloud** using the environment variables `TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`, and `TEMPORAL_API_KEY`. Do **not** mock Temporal.

## Implementation Hints
- Install the `temporalio` Python SDK.
- Use `temporalio.client.Client.connect(...)` with `tls=True` and the API key, address, and namespace from environment variables.
- Decorate the activity with `@activity.defn` and the workflow with `@workflow.defn` / `@workflow.run`.
- Inside the workflow, call `workflow.continue_as_new(new_start, target)` once the batch limit is reached. After calling it, the workflow run ends immediately.
- Use `workflow.execute_activity(...)` (with an appropriate `start_to_close_timeout`) to invoke the activity; do not block the workflow on raw I/O.
- Open `/workspace/loop.log` in append mode (`"a"`) inside the activity so that multiple workflow runs continue to extend the same file.
- Read the `ZEALT_RUN_ID` environment variable to scope the workflow id (`loop-py-${ZEALT_RUN_ID}`) so concurrent runs do not collide.
- The Worker must be running while the client triggers the workflow. Run the worker as a separate process or background task on the task queue `loop-py`.

## Acceptance Criteria
- Project path: `/home/user/loop-py`
- Task queue: `loop-py`
- Workflow id: `loop-py-${ZEALT_RUN_ID}` where `ZEALT_RUN_ID` is read from the environment.
- Workflow type name: `LongLoopWorkflow`
- The workflow source code must use the Temporal `continue_as_new` API (the literal substring `continue_as_new` must appear in the workflow source file).
- Log file: `/workspace/loop.log` — must contain exactly the 25 lines `1`, `2`, ..., `25`, each followed by `\n`, after the client completes.
- Output file: `/workspace/loop.out` — must contain a line `result=25` after the client completes.
- The final workflow run for workflow id `loop-py-${ZEALT_RUN_ID}` must reach status `COMPLETED` on Temporal Cloud with an integer result of `25`.
- There must be at least 2 prior runs in the same Workflow Execution chain that ended with status `CONTINUED_AS_NEW` (i.e., the workflow continued-as-new at least twice before finishing).
- The client must use the real Temporal Cloud connection (`TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`, `TEMPORAL_API_KEY`). Mocking the Temporal client or server is not allowed.

