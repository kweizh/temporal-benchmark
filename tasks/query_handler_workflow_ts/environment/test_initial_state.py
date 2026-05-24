import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_npx_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_workspace_dir_exists():
    assert os.path.isdir("/workspace"), "/workspace directory does not exist."


def test_temporal_env_vars_present():
    for var in ("TEMPORAL_API_KEY", "TEMPORAL_ADDRESS", "TEMPORAL_NAMESPACE"):
        assert os.environ.get(var), f"Required Temporal environment variable {var} is missing or empty."


def test_zealt_run_id_present():
    assert os.environ.get("ZEALT_RUN_ID"), "ZEALT_RUN_ID environment variable is missing or empty."


def test_temporalio_workflow_sdk_installed():
    result = subprocess.run(
        ["node", "-e", "require.resolve('@temporalio/workflow')"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"@temporalio/workflow is not resolvable from {PROJECT_DIR}: {result.stderr}"
    )


def test_temporalio_client_sdk_installed():
    result = subprocess.run(
        ["node", "-e", "require.resolve('@temporalio/client')"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"@temporalio/client is not resolvable from {PROJECT_DIR}: {result.stderr}"
    )


def test_temporalio_worker_sdk_installed():
    result = subprocess.run(
        ["node", "-e", "require.resolve('@temporalio/worker')"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"@temporalio/worker is not resolvable from {PROJECT_DIR}: {result.stderr}"
    )


def test_temporalio_activity_sdk_installed():
    result = subprocess.run(
        ["node", "-e", "require.resolve('@temporalio/activity')"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"@temporalio/activity is not resolvable from {PROJECT_DIR}: {result.stderr}"
    )
