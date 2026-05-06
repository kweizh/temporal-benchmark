import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"

def test_python_available():
    assert shutil.which("python") is not None or shutil.which("python3") is not None, "python binary not found in PATH."

def test_temporal_cli_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_temporal_server_running():
    try:
        result = subprocess.run(
            ["temporal", "operator", "cluster", "health"],
            capture_output=True,
            text=True,
            check=True
        )
        assert "SERVING" in result.stdout or "SERVING" in result.stderr or result.returncode == 0, "Temporal server is not healthy."
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Temporal server is not running or not healthy. Error: {e.stderr}")
