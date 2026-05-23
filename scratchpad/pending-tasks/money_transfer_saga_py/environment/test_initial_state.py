import json
import os

import pytest

PROJECT_DIR = "/home/user/myproject"
ACCOUNTS_FILE = "/workspace/accounts.json"


def test_temporalio_sdk_importable():
    try:
        import temporalio  # noqa: F401
        import temporalio.client  # noqa: F401
        import temporalio.worker  # noqa: F401
        import temporalio.activity  # noqa: F401
        import temporalio.workflow  # noqa: F401
    except Exception as e:  # pragma: no cover - import error path
        pytest.fail(f"temporalio Python SDK is not importable: {e}")


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_workspace_directory_exists():
    assert os.path.isdir("/workspace"), (
        "/workspace directory does not exist; it is required for the state file."
    )


def test_initial_accounts_file_exists():
    assert os.path.isfile(ACCOUNTS_FILE), (
        f"Initial state file {ACCOUNTS_FILE} does not exist."
    )


def test_initial_accounts_file_contents():
    with open(ACCOUNTS_FILE) as f:
        data = json.load(f)
    assert isinstance(data, dict), (
        f"{ACCOUNTS_FILE} must contain a JSON object, got {type(data).__name__}."
    )
    assert data.get("A") == 100, (
        f"Initial balance for account A must be 100, got {data.get('A')!r}."
    )
    assert data.get("B") == 0, (
        f"Initial balance for account B must be 0, got {data.get('B')!r}."
    )


def test_temporal_cloud_env_vars_present():
    for var in ("TEMPORAL_ADDRESS", "TEMPORAL_NAMESPACE", "TEMPORAL_API_KEY"):
        assert os.environ.get(var), (
            f"Required Temporal Cloud env var {var} is not set in the environment."
        )


def test_zealt_run_id_env_var_present():
    assert os.environ.get("ZEALT_RUN_ID"), (
        "Required ZEALT_RUN_ID env var is not set in the environment."
    )
