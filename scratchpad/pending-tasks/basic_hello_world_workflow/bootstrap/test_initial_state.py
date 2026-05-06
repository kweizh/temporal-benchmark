import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"

def test_temporal_cli_available():
    assert shutil.which("temporal") is not None, "Temporal CLI not found in PATH."

def test_python_available():
    assert shutil.which("python") is not None, "Python not found in PATH."

def test_temporalio_installed():
    try:
        subprocess.run(
            ["python", "-c", "import temporalio"],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        pytest.fail(f"temporalio package is not installed or cannot be imported. Error: {e.stderr}")

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_temporal_server_running():
    try:
        result = subprocess.run(
            ["temporal", "operator", "cluster", "health"],
            check=True,
            capture_output=True,
            text=True
        )
        assert "SERVING" in result.stdout or "status" in result.stdout.lower(), "Temporal server does not appear to be healthy."
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Temporal server is not running or not accessible. Error: {e.stderr}")
