import os
import shutil
import pytest

PROJECT_DIR = "/home/user/project"

def test_python_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."

def test_pytest_available():
    assert shutil.which("pytest") is not None, "pytest binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_activity_file_exists():
    activity_path = os.path.join(PROJECT_DIR, "activity.py")
    assert os.path.isfile(activity_path), f"Activity file {activity_path} does not exist."

def test_workflow_file_exists():
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    assert os.path.isfile(workflow_path), f"Workflow file {workflow_path} does not exist."

def test_test_workflow_file_exists():
    test_path = os.path.join(PROJECT_DIR, "test_workflow.py")
    assert os.path.isfile(test_path), f"Test file {test_path} does not exist."
