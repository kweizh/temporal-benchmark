import os
import shutil

PROJECT_DIR = "/home/user/myproject"
WORKSPACE_DIR = "/workspace"
WORKFLOW_FILE = os.path.join(PROJECT_DIR, "src", "workflows.ts")


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_package_json_exists():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json), (
        f"Starter package.json {package_json} must exist in the project directory."
    )


def test_workflow_file_exists():
    assert os.path.isfile(WORKFLOW_FILE), (
        f"Starter workflow file {WORKFLOW_FILE} must exist so the agent can "
        "refactor LongLoopWorkflow to use continueAsNew."
    )


def test_workspace_dir_exists():
    assert os.path.isdir(WORKSPACE_DIR), (
        f"Workspace directory {WORKSPACE_DIR} must exist so the incrementCounter "
        "activity can append to /workspace/loop.log."
    )


def test_temporal_api_key_env_set():
    value = os.environ.get("TEMPORAL_API_KEY")
    assert value is not None and value != "", (
        "TEMPORAL_API_KEY environment variable must be set in the task environment."
    )


def test_temporal_address_env_set():
    value = os.environ.get("TEMPORAL_ADDRESS")
    assert value is not None and value != "", (
        "TEMPORAL_ADDRESS environment variable must be set in the task environment."
    )


def test_temporal_namespace_env_set():
    value = os.environ.get("TEMPORAL_NAMESPACE")
    assert value is not None and value != "", (
        "TEMPORAL_NAMESPACE environment variable must be set in the task environment."
    )


def test_zealt_run_id_env_set():
    value = os.environ.get("ZEALT_RUN_ID")
    assert value is not None and value != "", (
        "ZEALT_RUN_ID environment variable must be set in the task environment."
    )
