import os
import shutil

PROJECT_DIR = "/home/user/myproject"
WORKSPACE_DIR = "/workspace"


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_pip3_available():
    assert shutil.which("pip3") is not None, "pip3 binary not found in PATH."


def test_temporalio_python_sdk_importable():
    try:
        import temporalio  # noqa: F401
        import temporalio.client  # noqa: F401
        import temporalio.worker  # noqa: F401
        import temporalio.workflow  # noqa: F401
        import temporalio.activity  # noqa: F401
    except Exception as exc:
        raise AssertionError(
            f"Temporal Python SDK (temporalio) must be importable, got: {exc!r}"
        )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_workspace_dir_exists():
    assert os.path.isdir(WORKSPACE_DIR), f"Workspace directory {WORKSPACE_DIR} does not exist."


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
