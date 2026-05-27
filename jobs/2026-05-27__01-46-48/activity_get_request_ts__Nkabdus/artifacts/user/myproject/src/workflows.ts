/**
 * workflows.ts
 *
 * Workflow code runs inside Temporal's deterministic sandbox.
 * It MUST NOT perform any I/O or use non-deterministic APIs directly.
 * All side-effects (HTTP calls, DB writes, etc.) must be delegated to Activities.
 *
 * The `proxyActivities` helper creates a type-safe proxy that, when called inside
 * a workflow, schedules an activity execution on a Worker rather than running
 * the function inline.
 */

import { proxyActivities } from '@temporalio/workflow';

// Import only the *type* of the activities module so that the workflow bundle
// never accidentally pulls in Node.js-only code (e.g. `fetch`, `fs`, etc.).
import type * as activities from './activities';

// Create a proxy for the activities. Temporal requires that every activity
// invocation has either `startToCloseTimeout` or `scheduleToCloseTimeout` set.
// 30 seconds is generous for a lightweight HTTP call.
const { fetchData } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
  retry: {
    maximumAttempts: 3,
  },
});

/**
 * FetchUrlWorkflow — accepts a URL, delegates the HTTP GET to the `fetchData`
 * activity, and returns the response body string to the caller.
 *
 * The workflow is kept deliberately thin: its only job is orchestration.
 */
export async function FetchUrlWorkflow(url: string): Promise<string> {
  const result = await fetchData(url);
  return result;
}
