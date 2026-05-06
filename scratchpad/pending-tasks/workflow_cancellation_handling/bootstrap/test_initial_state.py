import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/myproject"

def test_temporal_binary_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_temporal_server_running():
    try:
        result = subprocess.run(["temporal", "operator", "cluster", "health"], capture_output=True, text=True, timeout=5)
        assert result.returncode == 0, "Temporal server is not running or not healthy."
    except Exception as e:
        pytest.fail(f"Failed to check temporal server health: {e}")
