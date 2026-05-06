import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/subscription"

def test_temporal_binary_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_temporal_server_running():
    result = subprocess.run(
        ["temporal", "operator", "cluster", "health"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Temporal server is not running: {result.stderr}"
