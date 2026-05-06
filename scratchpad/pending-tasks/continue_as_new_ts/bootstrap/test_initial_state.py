import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_workflows_file_exists():
    workflows_path = os.path.join(PROJECT_DIR, "src", "workflows.ts")
    assert os.path.isfile(workflows_path), f"Workflows file {workflows_path} does not exist."

def test_initial_workflow_does_not_use_continue_as_new():
    workflows_path = os.path.join(PROJECT_DIR, "src", "workflows.ts")
    with open(workflows_path) as f:
        content = f.read()
    assert "processItemsWorkflow" in content, "Expected 'processItemsWorkflow' in workflows.ts."
    assert "continueAsNew" not in content, "Expected initial workflows.ts to not use 'continueAsNew'."
