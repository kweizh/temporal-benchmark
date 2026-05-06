import os
import shutil
import pytest

def test_python_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."

def test_temporal_cli_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir("/home/user/retry_project"), "Project directory /home/user/retry_project does not exist."
