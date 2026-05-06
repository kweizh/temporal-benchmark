import os
import shutil
import pytest

PROJECT_DIR = "/home/user/temporal-project"

def test_python_available():
    assert shutil.which("python3") is not None, "python3 not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_workflow_file_exists_and_has_datetime_now():
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    assert os.path.isfile(workflow_path), f"Workflow file {workflow_path} does not exist."
    with open(workflow_path, "r") as f:
        content = f.read()
    assert "datetime.now()" in content, "Expected initial workflow.py to use datetime.now()."
    assert "workflow.now()" not in content, "Expected initial workflow.py to not use workflow.now()."
