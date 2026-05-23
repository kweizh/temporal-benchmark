import json
import os
import subprocess

import pytest


WORKSPACE = "/workspace"
PROGRESS_JSON = os.path.join(WORKSPACE, "progress.json")
PROGRESS_LOG = os.path.join(WORKSPACE, "progress.log")


def _run_id():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is missing or empty."
    return run_id


def test_progress_json_exists_and_is_partial():
    assert os.path.isfile(PROGRESS_JSON), (
        f"Expected mid-run query output at {PROGRESS_JSON}, but it does not exist."
    )
    with open(PROGRESS_JSON, "r") as f:
        raw = f.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        pytest.fail(f"{PROGRESS_JSON} is not valid JSON: {e}; content was: {raw!r}")
    assert isinstance(data, dict), (
        f"{PROGRESS_JSON} should contain a JSON object, got: {type(data).__name__}"
    )
    assert "progress" in data, (
        f"{PROGRESS_JSON} is missing the required 'progress' field; got keys: {list(data.keys())}"
    )
    progress = data["progress"]
    assert isinstance(progress, (int, float)) and not isinstance(progress, bool), (
        f"'progress' field must be a number, got {type(progress).__name__}: {progress!r}"
    )
    assert 0 < progress < 1, (
        "Mid-run query must observe partial progress strictly between 0 and 1 "
        f"(exclusive); got progress={progress}. This indicates the Query did not "
        "land while the workflow was in-flight."
    )


def test_progress_log_has_exactly_five_lines():
    assert os.path.isfile(PROGRESS_LOG), (
        f"Expected activity log at {PROGRESS_LOG}, but it does not exist."
    )
    with open(PROGRESS_LOG, "r") as f:
        lines = [ln.rstrip("\n") for ln in f.readlines() if ln.strip() != ""]
    assert len(lines) == 5, (
        f"Expected exactly 5 non-empty lines in {PROGRESS_LOG}, got {len(lines)}: {lines!r}"
    )
    for idx, line in enumerate(lines, start=1):
        expected = f"step {idx}"
        assert line.strip() == expected, (
            f"Line {idx} of {PROGRESS_LOG} should be {expected!r}, got {line!r}"
        )


def test_workflow_completed_on_temporal_cloud():
    run_id = _run_id()
    workflow_id = f"progress-{run_id}"

    for var in ("TEMPORAL_API_KEY", "TEMPORAL_ADDRESS", "TEMPORAL_NAMESPACE"):
        assert os.environ.get(var), f"Required Temporal env var {var} is missing."

    verifier_script = r"""
const { Connection, Client } = require('@temporalio/client');

async function main() {
  const workflowId = process.env.VERIFY_WORKFLOW_ID;
  if (!workflowId) {
    throw new Error('VERIFY_WORKFLOW_ID is not set');
  }
  const connection = await Connection.connect({
    address: process.env.TEMPORAL_ADDRESS,
    tls: true,
    apiKey: process.env.TEMPORAL_API_KEY,
    metadata: { 'temporal-namespace': process.env.TEMPORAL_NAMESPACE },
  });
  const client = new Client({
    connection,
    namespace: process.env.TEMPORAL_NAMESPACE,
  });
  const handle = client.workflow.getHandle(workflowId);
  const desc = await handle.describe();
  const result = await handle.result();
  const payload = {
    status: desc.status && desc.status.name ? desc.status.name : String(desc.status),
    taskQueue: desc.taskQueue,
    result: result,
  };
  process.stdout.write(JSON.stringify(payload));
  await connection.close();
}

main().catch((err) => {
  process.stderr.write(String(err && err.stack ? err.stack : err));
  process.exit(1);
});
"""

    env = os.environ.copy()
    env["VERIFY_WORKFLOW_ID"] = workflow_id

    project_dir = "/home/user/myproject"
    proc = subprocess.run(
        ["node", "-e", verifier_script],
        cwd=project_dir,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, (
        f"Temporal Cloud verifier script failed (rc={proc.returncode}).\n"
        f"STDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
    )

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"Verifier output was not valid JSON: {e}; stdout={proc.stdout!r}")

    status = payload.get("status", "")
    assert status == "COMPLETED", (
        f"Expected workflow {workflow_id} status COMPLETED, got: {status!r}"
    )

    task_queue = payload.get("taskQueue")
    assert task_queue == "progress-ts", (
        f"Expected workflow to be registered on task queue 'progress-ts', got: {task_queue!r}"
    )

    result = payload.get("result")
    assert isinstance(result, dict), (
        f"Workflow result must be an object; got: {type(result).__name__}: {result!r}"
    )
    assert result.get("progress") == 1 or result.get("progress") == 1.0, (
        f"Expected final progress=1.0, got: {result.get('progress')!r}"
    )
    assert result.get("currentStep") == 5, (
        f"Expected final currentStep=5, got: {result.get('currentStep')!r}"
    )
    assert result.get("total") == 5, (
        f"Expected final total=5, got: {result.get('total')!r}"
    )
