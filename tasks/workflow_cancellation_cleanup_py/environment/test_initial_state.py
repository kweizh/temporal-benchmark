import importlib
import os

import pytest

PROJECT_DIR = "/home/user/cancel-py"
WORKSPACE_DIR = "/workspace"


def test_temporalio_sdk_importable():
    try:
        importlib.import_module("temporalio")
    except ImportError as exc:
        pytest.fail(f"temporalio Python SDK is not importable: {exc}")


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_workspace_dir_exists():
    assert os.path.isdir(WORKSPACE_DIR), (
        f"Workspace directory {WORKSPACE_DIR} does not exist."
    )


def test_temporal_address_env_set():
    assert os.environ.get("TEMPORAL_ADDRESS"), (
        "TEMPORAL_ADDRESS environment variable is not set."
    )


def test_temporal_namespace_env_set():
    assert os.environ.get("TEMPORAL_NAMESPACE"), (
        "TEMPORAL_NAMESPACE environment variable is not set."
    )


def test_temporal_api_key_env_set():
    assert os.environ.get("TEMPORAL_API_KEY"), (
        "TEMPORAL_API_KEY environment variable is not set."
    )


def test_zealt_run_id_env_set():
    assert os.environ.get("ZEALT_RUN_ID"), (
        "ZEALT_RUN_ID environment variable is not set."
    )
