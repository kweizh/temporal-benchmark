import os
import shutil
import pytest

PROJECT_DIR = "/home/user/project"

def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_files_exist():
    for f in ["package.json", "tsconfig.json", "src/activities.ts", "src/workflows.ts"]:
        path = os.path.join(PROJECT_DIR, f)
        assert os.path.isfile(path), f"File {path} does not exist."

def test_initial_workflow_state():
    wf_path = os.path.join(PROJECT_DIR, "src/workflows.ts")
    with open(wf_path) as f:
        content = f.read()
    assert "chargeCustomer(orderId)" in content, "Expected initial workflow to call chargeCustomer."
    assert "patched" not in content, "Expected initial workflow NOT to use patched."
    assert "chargeCustomerV2" not in content or "chargeCustomerV2(orderId)" not in content, "Expected initial workflow NOT to call chargeCustomerV2."
