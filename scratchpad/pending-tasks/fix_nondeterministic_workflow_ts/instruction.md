# Fix a Non-Deterministic Temporal Workflow (TypeScript)

## Background
A teammate wrote a Temporal Workflow in TypeScript that picks a percentage discount for a user. The Workflow currently performs random number generation and reads wall-clock time directly inside the Workflow body, which violates Temporal's [deterministic execution constraints](https://docs.temporal.io/develop/typescript/workflows/basics#workflow-logic-requirements). Even when the TypeScript SDK provides deterministic replacements for some APIs, the team's coding standard forbids the bare use of `Math.random` and `new Date(` inside Workflow code so that the codebase remains explicit about side effects and replay-safety.

Your job is to refactor the broken Workflow so that:
- Time is obtained through Temporal's Workflow API (e.g. `workflow.now()`).
- Random selection of the discount happens inside an Activity called `pickDiscount` and is awaited from the Workflow.

The project is already wired to connect to Temporal Cloud using `TEMPORAL_API_KEY`, `TEMPORAL_ADDRESS`, and `TEMPORAL_NAMESPACE` environment variables. A Worker and Client driver are already provided.

## Requirements
- Refactor `src/workflows.ts` so that the `DiscountWorkflow(userId: string)` Workflow no longer contains the strings `Math.random` or `new Date(`.
- Add an Activity `pickDiscount()` (in `src/activities.ts`) that returns one of the integer percentages `[0, 5, 10, 15, 20]` chosen at random.
- The Workflow must invoke `pickDiscount` through `proxyActivities` (do not call it inline) and must record the decision time using `workflow.now()` (or another Workflow-safe time API).
- The Workflow must return an object of shape `{ userId: string, discount: number, decidedAt: number }` where `decidedAt` is a Unix epoch millisecond timestamp obtained from the Workflow time API.
- Start the Worker (`npm run worker`) and then run the client (`npm run client`) which starts the Workflow with id `discount-${ZEALT_RUN_ID}` on Task Queue `discount-ts` and waits for completion.
- The client must append the resulting discount to the log file `/home/user/myproject/output.log` in the format `Discount: <number>` after the Workflow completes successfully.

## Implementation Hints
- Read the existing `src/workflows.ts`, `src/activities.ts`, `src/worker.ts`, and `src/client.ts` to understand the layout before changing anything.
- The Temporal TypeScript SDK exposes `now()` from `@temporalio/workflow` which returns the deterministic Workflow time.
- Activities can use `Math.random` freely; only Workflow code is restricted.
- Read the `ZEALT_RUN_ID` environment variable in the client and use it to derive the Workflow id `discount-${ZEALT_RUN_ID}`.
- Verify your fix by running the Worker in one process and the client in another; the Workflow must reach the `COMPLETED` state in Temporal Cloud.

## Acceptance Criteria
- Project path: /home/user/myproject
- Log file: /home/user/myproject/output.log
- The Workflow with id `discount-${ZEALT_RUN_ID}` on Task Queue `discount-ts` must reach the `COMPLETED` state in Temporal Cloud (no `NonDeterministicError`).
- The Workflow execution history must include at least one `ActivityTaskScheduled` event whose Activity Type is `pickDiscount`.
- The file `src/workflows.ts` must NOT contain the strings `Math.random` or `new Date(` (regex check on raw file contents).
- The Workflow result's `discount` field must be one of `0`, `5`, `10`, `15`, or `20`.
- The log file must contain a line in the format: `Discount: <number>` where `<number>` is the discount returned by the Workflow.

