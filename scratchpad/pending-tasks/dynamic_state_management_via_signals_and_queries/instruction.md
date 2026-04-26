Workflows often need to be dynamically updated or queried while running, which Temporal handles asynchronously via Signals (writes) and synchronously via Queries (reads).

You need to implement a stateful "User Profile" Workflow that manages a user's subscription status. The workflow must define a Signal handler to update the status string and a Query handler to return the current status. 

**Constraints:**
- The workflow must remain open and running asynchronously until a specific `terminate` Signal is received.
- The Query handler must be named `get_status` and the Signal handler must be named `update_status`.
- Do NOT execute any Activities in this task; focus entirely on Workflow state mutation.