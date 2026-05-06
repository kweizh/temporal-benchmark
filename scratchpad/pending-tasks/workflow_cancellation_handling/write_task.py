import json

data = {
  "task_name": "workflow_cancellation_handling",
  "task_description": """# Temporal Workflow Cancellation Handling

## Background
In Temporal, workflows can be cancelled externally. When a workflow is cancelled, any running activities are also cancelled. If you need to perform cleanup operations (like calling a cleanup activity) after a cancellation, you must run that cleanup activity in a `nonCancellable` `CancellationScope`.

## Requirements
Create a Temporal TypeScript project that implements a workflow and two activities:
1. `longRunningActivity`: An activity that loops, sleeps, and sends heartbeats. It simulates a long process.
2. `cleanupActivity`: An activity that executes when the workflow is cancelled and writes a file to disk.
3. `cancellableWorkflow`: A workflow that executes `longRunningActivity`. If the workflow is cancelled, it catches the cancellation error and executes `cleanupActivity` using a `nonCancellable` scope before failing the workflow.

## Implementation Guide
1. Initialize a Node.js project in `/home/user/myproject`.
2. Install `@temporalio/workflow`, `@temporalio/activity`, `@temporalio/client`, `@temporalio/worker`, and `typescript`.
3. Create `src/activities.ts` with `longRunningActivity` (which should heartbeat every 100ms and run for a long time) and `cleanupActivity` (which should write "cleanup done" to `/home/user/myproject/cleanup_done.txt`).
4. Create `src/workflows.ts` with `cancellableWorkflow`. It should try to execute `longRunningActivity`. If an error occurs, check if it's a cancellation using `isCancellation(err)`. If so, run `cleanupActivity` inside `CancellationScope.nonCancellable(...)`, and then re-throw the error to fail the workflow.
5. Create `src/worker.ts` to host the worker.
6. Create `src/client.ts` which connects to the Temporal server, starts the workflow, waits 2 seconds, cancels the workflow using `handle.cancel()`, and catches the resulting failure.

## Constraints
- Project path: `/home/user/myproject`
- Use TypeScript.
- The Temporal dev server is already running on `localhost:7233`.
- You must create `tsconfig.json` to compile the TypeScript code.
- The client script must be able to run and exit successfully after cancelling the workflow.

## Integrations
- None""",
  "truth": """# Verification Plan

## Setup
1. `cd /home/user/myproject`
2. `npm install`
3. `npx tsc`
4. `node dist/worker.js &`
5. Wait 2 seconds for worker to initialize.

## Verification Steps
1. Run `node dist/client.js`.
2. Verify that `/home/user/myproject/cleanup_done.txt` exists and contains "cleanup done".

## Specific Test Data
- None

## Expected Results
- The client script successfully cancels the workflow.
- The workflow handles the cancellation and executes the cleanup activity.
- The cleanup activity writes the file `/home/user/myproject/cleanup_done.txt`.

## Integrations
- None"""
}

with open("bootstrap/task.json", "w") as f:
    json.dump(data, f, indent=2)
