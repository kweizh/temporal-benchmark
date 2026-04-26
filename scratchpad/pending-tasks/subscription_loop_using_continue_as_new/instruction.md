Long-running workflows (e.g., monthly SaaS billing) can accumulate bloated event histories over years, potentially exceeding Temporal's hard limits if they loop infinitely in a single execution.

You need to write a Subscription Workflow that executes a `charge_monthly_fee` Activity, pauses for 30 days, and then restarts itself using Temporal's `ContinueAsNew` feature to truncate the event history and begin the next billing cycle.

**Constraints:**
- Must use the SDK's built-in `continue_as_new` mechanism at the end of the execution.
- You must use the deterministic workflow sleep function (e.g., awaiting `asyncio.sleep` within the Temporal Python workflow context) for the 30-day wait.
- Ensure the workflow increments and passes the current billing cycle count to the next run.