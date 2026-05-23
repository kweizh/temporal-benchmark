# Hello World Temporal Workflow (Python)

## Background
You are building your first Temporal application using the Temporal.io Python SDK (`temporalio`). The goal is to connect to **Temporal Cloud** using an API key, run a Worker that hosts a simple Workflow and Activity, and use a Client to start the Workflow and print its result.

Temporal Cloud credentials are already provided to the environment as the following variables: `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE`. Do **NOT** hard-code or invent credentials; read them from the environment.

## Requirements
- Implement a Python Temporal project that contains:
  - An **Activity** named `greet` that takes a string `name` and returns `Hello, <name>!`.
  - A **Workflow** named `HelloWorkflow` that accepts a string `name`, calls the `greet` activity, and returns its result.
  - A **Worker** that connects to Temporal Cloud (via API key + TLS) and polls the task queue `hello-world-py`.
  - A **Client** entrypoint that connects to Temporal Cloud, executes `HelloWorkflow` with the input `"Temporal"`, waits for completion, and prints the returned greeting to stdout.
- The Workflow ID must use the prefix `hello-py-` and include the current `run-id` so concurrent runs do not collide (e.g. `hello-py-${ZEALT_RUN_ID}`).
- The Worker and Client must use the task queue `hello-world-py`.
- Provide a `run.sh` start script that starts the Worker in the background, runs the Client, waits for the workflow result, prints it, and then exits cleanly (the Worker may be terminated after the Client finishes).

## Implementation Hints
- Install the official Python SDK package: `temporalio`.
- Use `temporalio.client.Client.connect(target, namespace=..., api_key=..., tls=True)` to connect to Temporal Cloud from both the Worker and Client.
- Define the Activity with the `@activity.defn` decorator and the Workflow with the `@workflow.defn` decorator (use `workflow.execute_activity` from inside the workflow with a reasonable `start_to_close_timeout`).
- Read `ZEALT_RUN_ID`, `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE` from `os.environ`.
- The Worker should be started with `temporalio.worker.Worker(client, task_queue=..., workflows=[...], activities=[...])` and call `await worker.run()`.
- Use `client.execute_workflow(HelloWorkflow.run, "Temporal", id=..., task_queue="hello-world-py")` from the Client to start the workflow and await its result.
- You can run the worker in the background of the same `run.sh` script (for example with a shell `&` and `kill` after the client finishes) - just make sure the workflow completes and its result is printed before the script exits.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: `bash run.sh` (executed from `/home/user/myproject`)
- Task queue: `hello-world-py`
- Workflow type name: `HelloWorkflow`
- Activity type name: `greet`
- Workflow ID: must start with `hello-py-` and include the value of the `ZEALT_RUN_ID` environment variable
- When `bash run.sh` is executed, the workflow `HelloWorkflow` must be started against Temporal Cloud using the namespace from `TEMPORAL_NAMESPACE`, run to completion, and the resulting greeting string returned from the activity must be printed to stdout.
- The completed workflow execution must be visible in Temporal Cloud (status `COMPLETED`) and its result must equal the greeting produced by the `greet` activity for the input `"Temporal"`.

