# HTTP GET Activity Workflow (Python)

## Background
You are building a basic Temporal.io application using the **Python SDK** that demonstrates the most fundamental Activity pattern: invoking a real HTTP API from inside a Temporal Activity and returning the response body to the Workflow. The Workflow orchestrates the execution, while the Activity performs the non-deterministic network I/O.

Temporal Cloud credentials are already provided to the environment as the following variables: `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE`. Do **NOT** hard-code or invent credentials; read them from the environment.

## Requirements
- Implement a Python Temporal project under `/home/user/myproject` that contains:
  - An **Activity** named `fetch_data` that takes a single `str` argument `url` and:
    - Performs an HTTP `GET` against the provided URL using a real HTTP client (e.g. `httpx` or `aiohttp`).
    - Returns the response body as a `str` (the decoded text body).
    - Must NOT mock the HTTP request — a real network call must be made.
  - A **Workflow** named `FetchUrlWorkflow` whose `run` method takes no arguments and:
    - Invokes the `fetch_data` Activity with the URL `https://api.github.com/zen`.
    - Returns the activity's return value (a string) as the workflow result.
  - A **Worker** that connects to Temporal Cloud (API key + TLS) and polls the task queue `fetch-url-py`, registering both the workflow and the activity.
  - A **Client** entrypoint that connects to Temporal Cloud, starts (or executes) `FetchUrlWorkflow`, waits for completion, and prints the returned string to stdout.
- The Workflow ID must be exactly `fetch-wf-${ZEALT_RUN_ID}`, where `${ZEALT_RUN_ID}` is read from the `ZEALT_RUN_ID` environment variable.
- The Worker and Client must both use the task queue `fetch-url-py`.
- Provide a startup mechanism so a single shell command can spin up the worker, run the client, wait for the workflow's result, print it to stdout, and exit cleanly with code `0`.

## Implementation Hints
- Install the official Python SDK: `pip install temporalio`. An HTTP client such as `httpx` is already available in the environment.
- Use `temporalio.client.Client.connect(address, namespace=..., api_key=..., tls=True)` for the client.
- Use `temporalio.worker.Worker(client, task_queue=..., workflows=[...], activities=[...])` for the worker.
- Activities can perform arbitrary I/O — that is exactly what they exist for. Do the HTTP call inside `fetch_data`, NOT inside the workflow function.
- From the workflow, use `workflow.execute_activity(fetch_data, "https://api.github.com/zen", start_to_close_timeout=timedelta(seconds=...))` to invoke the activity.
- Read `ZEALT_RUN_ID`, `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE` from `os.environ`.
- You can launch the worker as a background task in the same process (e.g., `asyncio.create_task(worker.run())`) and shut it down after the client finishes, or run it as a separate process — either approach is acceptable as long as the entrypoint exits cleanly with the printed result.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: `python3 main.py` (executed from `/home/user/myproject`)
- Task queue: `fetch-url-py`
- Workflow type name: `FetchUrlWorkflow`
- Activity type name: `fetch_data`
- Workflow ID: must equal `fetch-wf-${ZEALT_RUN_ID}` (read `ZEALT_RUN_ID` from the environment).
- When `python3 main.py` is executed, the workflow `FetchUrlWorkflow` must be started against Temporal Cloud using the namespace from `TEMPORAL_NAMESPACE`, run to completion, and the resulting string returned from the activity must be printed to stdout.
- The completed workflow execution must be visible in Temporal Cloud (status `COMPLETED`) and its result must be a non-empty string (the response body of `GET https://api.github.com/zen`).

