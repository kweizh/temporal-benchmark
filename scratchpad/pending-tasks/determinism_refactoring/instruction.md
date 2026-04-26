Temporal workflows must be strictly deterministic to allow for safe event history replay. Using standard system time or random number generators directly inside a workflow causes a `NondeterminismError` during recovery.

You need to refactor a broken Python Workflow that currently uses `datetime.now()` and `uuid.uuid4()` to generate a unique timestamped record ID. Replace these non-deterministic calls with Temporal's deterministic equivalents.

**Constraints:**
- You must replace standard library imports with `workflow.now()` and `workflow.uuid4()` from the `temporalio` SDK.
- Do NOT modify the input parameters, return type, or overall logic flow of the workflow.