In distributed systems, a failure in a later step requires rolling back earlier successful steps since atomicity cannot be guaranteed via traditional database transactions.

You need to implement a Saga execution inside a Money Transfer Workflow. The workflow must first execute a `withdraw_funds` Activity. If the subsequent `deposit_funds` Activity fails, the workflow must catch the failure and immediately execute a `refund_funds` compensation Activity.

**Constraints:**
- The compensation Activity (`refund_funds`) must be triggered in the workflow's exception handling block (e.g., `try/except ActivityError`).
- The workflow must ultimately re-raise the original exception after the compensation successfully completes.
- Assume the Activities are already defined; write only the Orchestration (Workflow) logic.