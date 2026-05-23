# Temporal Retry Policy: Fixed-Interval Activity Retries

## Background
You are extending a Temporal TypeScript project that already wires up a connection to a real Temporal Cloud namespace using `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE`. The skeleton provides a Worker and a Client script, but the Workflow and Activity implementations are missing. Your job is to configure a deliberately flaky Activity together with a custom Activity RetryPolicy so that the Workflow retries the Activity a fixed number of times with a fixed delay, observes the eventual failure, and converts it into a graceful workflow return value.

## Requirements
- Implement an Activity in `src/activities.ts` named `flakyTask` that:
  - Appends a single line to `/workspace/attempts.log` on every invocation (one line per attempt). Each line must include the current attempt number, but the exact line format is up to you.
  - Always fails by throwing a Temporal `ApplicationFailure` (retryable, i.e. `nonRetryable` must NOT be set to `true`).
- Implement a Workflow in `src/workflows.ts` named `FlakyWorkflow` that:
  - Proxies `flakyTask` with `startToCloseTimeout: '30 seconds'` and a custom Activity `RetryPolicy` of `maximumAttempts: 5`, `initialInterval: '2 seconds'`, and `backoffCoefficient: 1.0` (so the delay stays fixed at 2 seconds between attempts).
  - Catches the eventual Activity failure once retries are exhausted and returns the string `"failed after 5 attempts"`. The Workflow itself must complete successfully (status `COMPLETED`), not fail.
- Do NOT modify the existing connection / worker / client code in `src/worker.ts` or `src/client.ts`. The Worker registers activities from `./activities`, bundles workflows from `./workflows`, and polls the `retry-ts` task queue.
- Running `npm run client` must start the Workflow against Temporal Cloud and write the returned string to a log file.

## Implementation Hints
- Use `proxyActivities<typeof activities>({ startToCloseTimeout: '30 seconds', retry: { maximumAttempts: 5, initialInterval: '2 seconds', backoffCoefficient: 1.0 } })` to get a typed handle to the activity inside the Workflow.
- Inside the Workflow, wrap the activity call in `try { ... } catch (err) { return 'failed after 5 attempts'; }` so that the Workflow returns instead of failing once retries are exhausted.
- For attempt accounting inside the activity, you can rely on `Context.current().info.attempt` from `@temporalio/activity`. The activity must append exactly one line to `/workspace/attempts.log` per invocation.
- Throw a Temporal `ApplicationFailure` (imported from `@temporalio/common` or `@temporalio/activity`) so the failure is treated as retryable by the Activity RetryPolicy. Do NOT mark the failure as `nonRetryable`.
- The Workflow ID must be `retry-${ZEALT_RUN_ID}` so concurrent runs do not collide, and the workflow must be started on the `retry-ts` task queue.
- Use the existing `npm run worker` and `npm run client` scripts in `package.json` to start the Worker and trigger execution.

## Acceptance Criteria
- Project path: /home/user/myproject
- Log file: /home/user/myproject/output.log
- Attempt log file: /workspace/attempts.log
- Read `run-id` from the `ZEALT_RUN_ID` environment variable.
- A Workflow Execution must be created on Temporal Cloud (namespace `$TEMPORAL_NAMESPACE`) with:
  - Workflow Type: `FlakyWorkflow`
  - Workflow ID: `retry-${ZEALT_RUN_ID}`
  - Task Queue: `retry-ts`
- The Workflow Execution must complete with status `COMPLETED` and a string result equal to `failed after 5 attempts`.
- After running `npm run client`, the log file `/home/user/myproject/output.log` must contain a line in the format: `Workflow result: failed after 5 attempts`.
- The file `/workspace/attempts.log` must exist and contain exactly 5 lines (one per Activity attempt).

