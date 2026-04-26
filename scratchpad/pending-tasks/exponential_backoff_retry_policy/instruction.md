Temporal handles retries automatically for Activities, but default configurations often need to be tuned to prevent unnecessary delays or excessive retries.

You need to implement a Python Temporal Workflow that executes a `process_data` Activity. The Workflow must configure the Activity call with a `RetryPolicy` that attempts execution exactly 3 times, with an initial interval of 2 seconds and a backoff coefficient of 2.0. 

**Constraints:**
- Must use the Python SDK (`temporalio.workflow` and `temporalio.common.RetryPolicy`).
- The Activity execution must be configured with a `start_to_close_timeout` of 10 seconds.
- Do NOT write the Worker initialization code; provide only the Activity definition and Workflow class.