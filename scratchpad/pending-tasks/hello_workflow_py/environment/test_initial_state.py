import os
import shutil

PROJECT_DIR = "/home/user/myproject"


def test_python_available():
    assert shutil.which("python") is not None or shutil.which("python3") is not None, \
        "python/python3 binary not found in PATH."


def test_pip_available():
    assert shutil.which("pip") is not None or shutil.which("pip3") is not None, \
        "pip/pip3 binary not found in PATH."


def test_temporalio_importable():
    import temporalio  # noqa: F401
    import temporalio.client  # noqa: F401
    import temporalio.worker  # noqa: F401
    import temporalio.workflow  # noqa: F401
    import temporalio.activity  # noqa: F401


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


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
