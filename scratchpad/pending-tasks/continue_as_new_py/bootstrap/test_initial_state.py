import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"

def test_temporal_binary_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_temporalio_installed():
    result = subprocess.run(["python3", "-c", "import temporalio"], capture_output=True)
    assert result.returncode == 0, "temporalio Python SDK is not installed."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_workflow_file_exists():
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    assert os.path.isfile(workflow_path), f"Workflow file {workflow_path} does not exist."

def test_initial_workflow_content():
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    with open(workflow_path, "r") as f:
        content = f.read()
    assert "class ProcessItemsWorkflow:" in content, "ProcessItemsWorkflow class not found in workflow.py"
    assert "def run(self, start_index: int, total_items: int)" in content, "run method signature not found"
    assert "continue_as_new" not in content, "continue_as_new should not be present in the initial state"
