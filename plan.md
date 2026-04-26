### 1. Library Overview
*   **Description**: Temporal is an open-source durable execution platform that enables developers to build "invincible" applications. It abstracts away the complexity of distributed systems (retries, state management, timeouts, and coordination) by providing a programming model where code is automatically fault-tolerant and stateful.
*   **Ecosystem Role**: It acts as a workflow orchestration engine. It sits between your application services, managing long-running processes that can last from seconds to years. It is frequently used for payment processing, SaaS provisioning, background jobs, and increasingly for "agentic" AI workflows where multi-step LLM operations must be reliable.
*   **Project Setup**:
    1.  **Install Temporal CLI**: `curl -sSf https://temporal.download/cli.sh | sh` (or `brew install temporal`).
    2.  **Start Local Server**: `temporal server start-dev` (runs the server and Web UI at `http://localhost:8233`).
    3.  **SDK Installation**:
        *   **Python**: `pip install temporalio`
        *   **TypeScript**: `npm install @temporalio/workflow @temporalio/activity @temporalio/client @temporalio/worker`
    4.  **Boilerplate**: Typically involves defining an `Activity`, a `Workflow` that calls that activity, and a `Worker` to host them.
### 2. Core Primitives & APIs
*   **Workflows**: Orchestration logic. **Must be deterministic.**
    *   *Python*: `@workflow.defn`, `@workflow.run`.
    *   *TypeScript*: Exported functions in a dedicated workflow file.
*   **Activities**: Side effects (API calls, DB ops). Can be non-deterministic and have retries.
    *   *Python*: `@activity.defn`.
    *   *TypeScript*: Exported functions.
*   **Workers**: Processes that listen to a "Task Queue" and execute the code.
*   **Signals & Queries**:
    *   **Signal**: Asynchronous "write" to a running workflow (e.g., `workflow.signal`).
    *   **Query**: Synchronous "read" of workflow state (e.g., `workflow.query`).
*   **Updates**: Synchronous "write-then-read" (Wait for a result from a signal-like call).
#### Code Snippet (Python)
```python
from temporalio import workflow, activity
from datetime import timedelta
@activity.defn
async def send_email(email: str) -> str:
    # Side effects go here
    return f"Email sent to {email}"
@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        # Orchestration logic (Deterministic!)        result = await workflow.execute_activity(
            send_email, 
            f"{name}@example.com", 
            start_to_close_timeout=timedelta(seconds=5)
        )
        return result
```
#### Documentation Links
*   [Workflows Concepts](https://docs.temporal.io/workflows)
*   [Activities Concepts](https://docs.temporal.io/activities)
*   [Python SDK Guide](https://docs.temporal.io/develop/python)
*   [TypeScript SDK Guide](https://docs.temporal.io/develop/typescript)
### 3. Real-World Use Cases & Templates
*   **Durable AI Agents**: Orchestrating multi-step LLM chains where each step (Activity) is retried on failure, and the state (Workflow) is preserved.
*   **Subscription Billing**: Managing monthly billing cycles with Timers and `ContinueAsNew` for infinite loops.
*   **Money Transfer**: Ensuring atomicity across distributed services (e.g., withdraw from A, deposit to B).
*   **Templates**:
    *   [Temporal Samples (GitHub)](https://github.com/temporalio/samples-python) - Official repository of patterns.
    *   [Subscription Pattern](https://github.com/temporalio/samples-typescript/tree/main/subscription) - Common SaaS billing example.
### 4. Developer Friction Points
*   **Determinism Violations**: Using `time.now()`, `random.uuid()`, or global variables inside a Workflow. This causes `NondeterminismError` during replay. [Issue Example](https://github.com/temporalio/sdk-go/issues/818).
*   **Versioning/Patching**: Modifying a Workflow's logic (e.g., adding a new activity) while instances are still running. If not handled with the `Patching API` or `GetVersion`, the replay will fail because the history doesn't match the new code.
*   **Activity Timeout Confusion**: Misunderstanding `StartToClose` (worker execution time) vs `ScheduleToClose` (total time including queue wait). Setting these too low causes unnecessary retries.
### 5. Evaluation Ideas
*   **Basic**: Implement a "Hello World" workflow and activity that returns a formatted string.
*   **Reliability**: Create a workflow that retries an activity 3 times with exponential backoff before failing.
*   **State Management**: Use a Signal to update a "User Profile" workflow's state while it is running.
*   **Determinism Fix**: Refactor a provided "broken" workflow that uses `datetime.now()` to use `workflow.now()`.
*   **Long-running**: Implement a "Subscription" workflow that sleeps for 30 days and uses `ContinueAsNew` to prevent history bloat.
*   **Versioning**: Safely add a second activity to an existing workflow using the SDK's versioning/patching API.
*   **Complex Coordination**: Implement a "Saga Pattern" where if a second activity fails, a compensation activity is triggered to roll back the first one.
### 6. Sources
1.  [Temporal Documentation (llms.txt)](https://docs.temporal.io/llms.txt) - Full platform documentation overview.
2.  [Temporal Python SDK README](https://github.com/temporalio/sdk-python) - Installation and basic usage for Python.
3.  [Temporal TypeScript SDK Guide](https://docs.temporal.io/develop/typescript) - Core concepts and setup for TypeScript.
4.  [Temporal Anti-Patterns Blog](https://temporal.io/blog/spooky-stories-chilling-temporal-anti-patterns-part-1) - Detailed discussion of common developer mistakes.
5.  [AI Agent Architecture with Temporal](https://www.waylandz.com/ai-agent-book-en/chapter-21-temporal-workflows/) - Modern use cases for LLM orchestration.
6.  [Determinism in Temporal](https://docs.temporal.io/workflows#determinism) - Official explanation of the determinism requirement.