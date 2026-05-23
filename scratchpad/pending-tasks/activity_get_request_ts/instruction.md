# Temporal Activity: HTTP GET against GitHub API

## Background
You are extending a Temporal TypeScript project that connects to Temporal Cloud. The project skeleton already wires up the Worker and a Client runner that starts a Workflow against Temporal Cloud. Your job is to implement the missing Activity and Workflow so that running the client triggers a Workflow Execution which calls an HTTP GET Activity, parses the response, and returns a string result. The Worker is configured to poll the `repo-fetch-ts` task queue using credentials from `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE`.

## Requirements
- Implement an Activity in `src/activities.ts` named `getRepoFullName` that performs an HTTP GET against `https://api.github.com/repos/temporalio/temporal` using Node's built-in `fetch`, parses the JSON body, and returns the `full_name` field as a string.
- Implement a Workflow in `src/workflows.ts` named `FetchRepoWorkflow` that proxies the activity with a `startToCloseTimeout` of `30 seconds` and returns the activity's result.
- Do NOT modify the existing connection / worker / client code (`src/worker.ts`, `src/client.ts`). The Worker registers activities from `./activities` and is bundled with workflows from `./workflows`.
- Running the client must start the Workflow against the real Temporal Cloud namespace and print the resulting string to stdout.

## Implementation Hints
- The activity must use Node 20's global `fetch` (no extra HTTP library needed) and return `data.full_name` from the parsed JSON.
- In the Workflow, import the activity types and use `proxyActivities<typeof activities>({ startToCloseTimeout: '30 seconds' })` to obtain a typed handle.
- The Worker polls the task queue `repo-fetch-ts`; the Workflow must be started on the same task queue.
- The Workflow ID must be `repo-fetch-${ZEALT_RUN_ID}` so concurrent runs do not collide.
- Use the existing `npm run worker` and `npm run client` scripts in `package.json` to start the Worker and trigger execution.

## Acceptance Criteria
- Project path: /home/user/myproject
- Log file: /home/user/myproject/output.log
- Read `run-id` from the `ZEALT_RUN_ID` environment variable.
- A Workflow Execution must be created on Temporal Cloud (namespace `$TEMPORAL_NAMESPACE`) with:
  - Workflow Type: `FetchRepoWorkflow`
  - Workflow ID: `repo-fetch-${ZEALT_RUN_ID}`
  - Task Queue: `repo-fetch-ts`
- The Workflow Execution must complete successfully with a string result equal to `temporalio/temporal`.
- After running `npm run client`, the log file `/home/user/myproject/output.log` must contain a line in the format: `Workflow result: temporalio/temporal`.

