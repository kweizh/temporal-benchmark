import os
import shutil
import pytest

PROJECT_DIR = "/home/user/temporal-project"

def test_temporal_binary_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_workflow_files_exist():
    for filename in ["workflow.py", "worker.py", "starter.py"]:
        file_path = os.path.join(PROJECT_DIR, filename)
        assert os.path.isfile(file_path), f"File {file_path} does not exist."