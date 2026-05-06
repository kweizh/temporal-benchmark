import os
import shutil
import pytest

PROJECT_DIR = "/home/user/temporal-project"

def test_temporal_cli_binary_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_project_files_exist():
    files_to_check = [
        "src/workflows.ts",
        "src/activities.ts",
        "src/worker.ts",
        "src/client.ts",
        "package.json",
        "tsconfig.json"
    ]
    for rel_path in files_to_check:
        full_path = os.path.join(PROJECT_DIR, rel_path)
        assert os.path.isfile(full_path), f"Expected file {full_path} does not exist."

def test_initial_workflow_content():
    workflows_path = os.path.join(PROJECT_DIR, "src/workflows.ts")
    with open(workflows_path, "r") as f:
        content = f.read()
    assert "alwaysFailActivity" in content, "Expected 'alwaysFailActivity' to be imported or referenced in workflows.ts."
    assert "retry" not in content or "maximumAttempts" not in content, "Workflow should not have the retry policy configured initially."
