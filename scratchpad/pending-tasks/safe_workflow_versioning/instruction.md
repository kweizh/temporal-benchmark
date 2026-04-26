Modifying a Workflow's orchestration logic while previous instances are still running breaks determinism for those in-flight workflows, requiring the use of Temporal's Versioning/Patching API.

You need to safely update an existing Workflow to add a new `send_notification` Activity immediately after an existing `process_order` Activity. Use the Temporal Patching API to ensure backward compatibility for workflows that started before the code change.

**Constraints:**
- Must use the official Temporal SDK patching API (e.g., `workflow.patched` in Python).
- The patch identifier must be strictly named `"add-notification-step"`.
- Old in-flight workflows must bypass the new activity, while newly started workflows must execute it.