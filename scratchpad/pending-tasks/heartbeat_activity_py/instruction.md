# Long-Running Activity with Heartbeats (Python)

## Background
You are building a long-running Activity using the Temporal.io **Python SDK**. The Activity counts iteratively up to a target value and reports its progress back to the Temporal Service by sending periodic Heartbeats. The Workflow that orchestrates the Activity must configure a `heartbeat_timeout` so the Temporal Service can detect a stuck or crashed Activity.

This exercises Temporal's **Heartbeat** primitive: an Activity must call `temporalio.activity.heartbeat(...)` regularly while it runs so the Temporal Service knows it is still alive. The Workflow side enforces this by setting a `heartbeat_timeout` on the activity invocation.

Temporal Cloud credentials are already provided to the environment as the following variables: `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE`. Do **NOT** hard-code or invent credentials; read them from the environment.

## Requirements
- Implement a Python Temporal project under `/home/user/myproject` that contains:
  - An **Activity** named `count_with_heartbeat` that takes a single `int` argument `target` and:
    - Iterates from `1` to `target` (inclusive).
    - For each iteration `i`, sleeps for about `0.5` seconds using `asyncio.sleep` and calls `temporalio.activity.heartbeat(i)` to report progress.
    - Returns the final integer count, which must equal `target`.
  - A **Workflow** named `HeartbeatWorkflow` whose `run` method accepts a single positional argument `target: int` and:
    - Invokes the `count_with_heartbeat` Activity with `heartbeat_timeout=timedelta(seconds=5)` and `start_to_close_timeout=timedelta(seconds=120)`.
    - Returns the integer count returned by the Activity.
  - A **Worker** that connects to Temporal Cloud (API key + TLS) and polls the task queue `heartbeat-py`, registering both the workflow and the activity.
  - A **Client** entrypoint that connects to Temporal Cloud, starts (or executes) `HeartbeatWorkflow` with `target=5`, waits for completion, and prints the returned integer to stdout.
- The Workflow ID must be exactly `heartbeat-wf-${ZEALT_RUN_ID}`, where `${ZEALT_RUN_ID}` is read from the `ZEALT_RUN_ID` environment variable.
- The Worker and Client must both use the task queue `heartbeat-py`.
- Provide a startup mechanism so a single shell command (`python main.py`) spins up the worker, runs the client, waits for the workflow's result, prints it, and exits cleanly with code 0.

## Implementation Hints
- Install the official Python SDK: `pip install temporalio`.
- Use `temporalio.client.Client.connect(address, namespace=..., api_key=..., tls=True)` for the client.
- Use `temporalio.worker.Worker(client, task_queue=..., workflows=[...], activities=[...])` for the worker.
- Inside the activity, call `temporalio.activity.heartbeat(i)` on every iteration; pair this with `await asyncio.sleep(0.5)` so the activity is long-running enough to demonstrate the heartbeat pattern.
- On the workflow side, use `workflow.execute_activity(count_with_heartbeat, target, start_to_close_timeout=timedelta(seconds=120), heartbeat_timeout=timedelta(seconds=5))`.
- You can launch the worker as a background task in the same process (e.g., `asyncio.create_task(worker.run())`) and shut it down after the client finishes, or run it as a separate process — either approach is acceptable as long as `python main.py` exits cleanly with the printed result.
- Read `ZEALT_RUN_ID`, `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE` from `os.environ`.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: `python main.py` (executed from `/home/user/myproject`)
- Task queue: `heartbeat-py`
- Workflow type name: `HeartbeatWorkflow`
- Activity type name: `count_with_heartbeat`
- Workflow ID: must equal `heartbeat-wf-${ZEALT_RUN_ID}` (read `ZEALT_RUN_ID` from the environment).
- The Workflow must invoke the Activity with a `heartbeat_timeout` of `timedelta(seconds=5)` and a `start_to_close_timeout` of `timedelta(seconds=120)`.
- When `python main.py` is executed from the project directory, the workflow `HeartbeatWorkflow` must be started against Temporal Cloud using the namespace from `TEMPORAL_NAMESPACE`, run to completion, and the integer count returned from the activity must be printed to stdout.
- The completed workflow execution must be visible in Temporal Cloud (status `COMPLETED`) and its result must equal the integer `5`. The execution's event history must contain at least one `ActivityTaskStarted` event, and the activity must complete without an activity timeout failure.

