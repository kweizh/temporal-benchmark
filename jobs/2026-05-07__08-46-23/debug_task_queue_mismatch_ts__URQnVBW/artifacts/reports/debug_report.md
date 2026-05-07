# Temporal Task Queue Mismatch Debug Report

## Issue
The workflow `MyWorkflow` was being started on task queue `my-task-queue` by the client, but the worker was listening on `wrong-task-queue`. This caused the workflow to stay in the 'Running' state indefinitely as no worker was picking up the tasks.

## Fix
Updated `src/worker.ts` to use the correct task queue name: `my-task-queue`.

## Verification
- Started Temporal server (dev mode).
- Started the worker: `npx ts-node src/worker.ts`.
- Ran the client: `npx ts-node src/client.ts`.
- Output:
  ```
  Started workflow my-workflow-id-735
  Hello, Temporal!
  ```
