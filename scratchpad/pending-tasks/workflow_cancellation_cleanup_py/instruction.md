# Graceful Workflow Cancellation with Shielded Cleanup (Temporal Python SDK)

## Background
Temporal Workflows can be canceled by clients. In Python, a cancellation is delivered to the workflow as an `asyncio.CancelledError` raised at the next `await` point. A well-written workflow can catch this exception, run any required cleanup (release locks, free resources, write audit logs), and then re-raise the error so the workflow is recorded as `CANCELED` on the server. Because cleanup work also runs inside the cancelled task, it must be **shielded** (e.g. with `asyncio.shield`) so the cancellation does not abort the cleanup itself. In this task you will implement this pattern end-to-end against **Temporal Cloud** using the **Python SDK**.

## Requirements
- Implement a Temporal Activity `release_resources(job_id: str)` in Python that appends a single line `released:<job_id>` to the file `/workspace/cleanup.log` (creating the file if necessary).
- Implement a Temporal Workflow `LongJobWorkflow` in Python that:
  - Takes a single argument `job_id: str` in its `@workflow.run` method.
  - Calls `await workflow.sleep(timedelta(minutes=10))` as its main work.
  - When cancellation is requested, catches `asyncio.CancelledError`, executes the `release_resources` activity for the given `job_id` in a way that survives cancellation (i.e. shields the activity invocation so it completes even though the workflow task itself has been cancelled), and then re-raises `asyncio.CancelledError` so the workflow ends in the `CANCELED` state.
- Implement a Worker that polls the task queue `cancel-py` and hosts both `LongJobWorkflow` and `release_resources`.
- Implement a Client script that:
  1. Connects to Temporal Cloud using `TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`, and `TEMPORAL_API_KEY`.
  2. Starts `LongJobWorkflow` with workflow id `job-${ZEALT_RUN_ID}`, task queue `cancel-py`, and the argument `job_id="alpha"`.
  3. Waits roughly 3 seconds, then calls `handle.cancel()` on the workflow handle.
  4. Awaits the workflow result and expects a cancellation (i.e. the awaited result raises a cancellation-related error). The client must not treat this as task failure: it should exit with status code `0` once the workflow has been confirmed as cancelled.
- Connect to **Temporal Cloud** using the environment variables `TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`, and `TEMPORAL_API_KEY`. Do **not** mock Temporal.
- Read `ZEALT_RUN_ID` from the environment and use it as the workflow id suffix so concurrent runs do not collide.

## Implementation Hints
- Install the `temporalio` Python SDK.
- Use `temporalio.client.Client.connect(address, namespace=..., api_key=..., tls=True)` for Temporal Cloud connections (API keys require TLS).
- Decorate the workflow with `@workflow.defn` and the activity with `@activity.defn`.
- Inside the workflow, wrap the long sleep in `try/except asyncio.CancelledError`. To make the cleanup activity invocation survive cancellation, schedule it with `workflow.execute_activity(...)` and wrap that coroutine in `asyncio.shield(...)` before awaiting. Re-raise the `CancelledError` from the `except` block once cleanup has completed.
- Give the cleanup activity a reasonable `start_to_close_timeout` (e.g. 30 seconds).
- The worker process must be running while the client cancels and awaits the workflow; run it as a separate process or as an `asyncio` background task on task queue `cancel-py`.
- When awaiting `handle.result()` after a cancel, the SDK raises a `WorkflowFailureError` whose cause is a `CancelledError`. Catch that case in the client and exit cleanly.

## Acceptance Criteria
- Project path: `/home/user/cancel-py`
- Task queue: `cancel-py`
- Workflow id: `job-${ZEALT_RUN_ID}` where `ZEALT_RUN_ID` is read from the environment.
- Workflow type name: `LongJobWorkflow`
- Activity type name: `release_resources`
- Output file: `/workspace/cleanup.log` — must contain a line `released:alpha` after the client completes.
- The workflow execution must reach status `CANCELED` on Temporal Cloud.
- The workflow event history must include at least one `ActivityTaskScheduled` event for the activity type `release_resources`.
- The client must use the real Temporal Cloud connection (`TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`, `TEMPORAL_API_KEY`). Mocking the Temporal client or server is not allowed.

