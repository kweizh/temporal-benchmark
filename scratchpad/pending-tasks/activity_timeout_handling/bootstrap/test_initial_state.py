import os
import shutil
import pytest

PROJECT_DIR = "/home/user/temporal_project"

def test_temporal_binary_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_python_binary_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_workflow_file_exists():
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    assert os.path.isfile(workflow_path), f"Workflow file {workflow_path} does not exist."

def test_run_workflow_file_exists():
    run_workflow_path = os.path.join(PROJECT_DIR, "run_workflow.py")
    assert os.path.isfile(run_workflow_path), f"Run workflow file {run_workflow_path} does not exist."

def test_initial_timeout_is_2_seconds():
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    with open(workflow_path) as f:
        content = f.read()
    assert "start_to_close_timeout=timedelta(seconds=2)" in content or "start_to_close_timeout = timedelta(seconds=2)" in content, \
        "Expected initial start_to_close_timeout to be 2 seconds in workflow.py."
