import os
import shutil
import pytest

PROJECT_DIR = "/home/user/project"

def test_temporal_binary_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_project_files_exist():
    expected_files = ["workflow.py", "worker.py", "starter.py", "interceptor.py"]
    for file in expected_files:
        file_path = os.path.join(PROJECT_DIR, file)
        assert os.path.isfile(file_path), f"Expected file {file_path} does not exist."
