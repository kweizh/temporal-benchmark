import os
import shutil
import pytest

PROJECT_DIR = "/home/user/project"

def test_node_installed():
    assert shutil.which("node") is not None, "node binary not found in PATH."
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_workflows_file_exists():
    workflows_path = os.path.join(PROJECT_DIR, "src", "workflows.ts")
    assert os.path.isfile(workflows_path), f"Workflows file {workflows_path} does not exist."

def test_initial_code_contains_nondeterminism():
    workflows_path = os.path.join(PROJECT_DIR, "src", "workflows.ts")
    with open(workflows_path, "r") as f:
        content = f.read()
    
    assert "new Date()" in content, "Expected 'new Date()' in workflows.ts initially."
    assert "globalDiscountState" in content, "Expected 'globalDiscountState' in workflows.ts initially."
