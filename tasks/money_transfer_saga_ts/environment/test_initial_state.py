import json
import os
import shutil

PROJECT_DIR = "/home/user/myproject"
WORKSPACE_DIR = "/workspace"
ACCOUNTS_FILE = "/workspace/accounts.json"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_workspace_dir_exists():
    assert os.path.isdir(WORKSPACE_DIR), (
        f"Workspace directory {WORKSPACE_DIR} must exist so the saga activities "
        "can read and write /workspace/accounts.json."
    )


def test_accounts_file_exists():
    assert os.path.isfile(ACCOUNTS_FILE), (
        f"Expected the initial balances file {ACCOUNTS_FILE} to exist before the task "
        "begins; the Dockerfile should pre-create it with the initial balances."
    )


def test_accounts_file_initial_balances():
    with open(ACCOUNTS_FILE, "r") as fh:
        data = json.load(fh)
    assert data.get("A") == 100, (
        f"Expected initial balance A == 100 in {ACCOUNTS_FILE}, got {data!r}."
    )
    assert data.get("B") == 0, (
        f"Expected initial balance B == 0 in {ACCOUNTS_FILE}, got {data!r}."
    )


def test_temporal_api_key_env_set():
    value = os.environ.get("TEMPORAL_API_KEY")
    assert value is not None and value != "", \
        "TEMPORAL_API_KEY environment variable must be set in the task environment."


def test_temporal_address_env_set():
    value = os.environ.get("TEMPORAL_ADDRESS")
    assert value is not None and value != "", \
        "TEMPORAL_ADDRESS environment variable must be set in the task environment."


def test_temporal_namespace_env_set():
    value = os.environ.get("TEMPORAL_NAMESPACE")
    assert value is not None and value != "", \
        "TEMPORAL_NAMESPACE environment variable must be set in the task environment."


def test_zealt_run_id_env_set():
    value = os.environ.get("ZEALT_RUN_ID")
    assert value is not None and value != "", \
        "ZEALT_RUN_ID environment variable must be set in the task environment."
