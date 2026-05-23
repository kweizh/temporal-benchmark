import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"


def test_temporalio_importable():
    try:
        importlib.import_module("temporalio")
    except ImportError as exc:
        pytest.fail(f"temporalio SDK is not importable: {exc}")


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_workspace_dir_exists():
    assert os.path.isdir("/workspace"), (
        "/workspace directory does not exist; it is required for log output."
    )


def test_attempts_log_not_yet_created():
    assert not os.path.exists("/workspace/attempts.log"), (
        "/workspace/attempts.log should not exist before the task starts."
    )


def test_result_log_not_yet_created():
    assert not os.path.exists("/workspace/result.log"), (
        "/workspace/result.log should not exist before the task starts."
    )


def test_required_env_vars_present():
    for var in ("TEMPORAL_ADDRESS", "TEMPORAL_NAMESPACE", "TEMPORAL_API_KEY", "ZEALT_RUN_ID"):
        assert os.environ.get(var), f"Environment variable {var} must be set."
