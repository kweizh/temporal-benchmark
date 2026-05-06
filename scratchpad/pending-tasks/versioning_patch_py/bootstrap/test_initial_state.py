import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/temporal_project"

def test_temporal_cli_available():
    assert shutil.which("temporal") is not None, "temporal CLI not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_workflow_file_exists():
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    assert os.path.isfile(workflow_path), f"Workflow file {workflow_path} does not exist."

def test_verify_replay_exists():
    verify_replay_path = os.path.join(PROJECT_DIR, "verify_replay.py")
    assert os.path.isfile(verify_replay_path), f"Verification script {verify_replay_path} does not exist."

def test_test_new_workflow_exists():
    test_new_workflow_path = os.path.join(PROJECT_DIR, "test_new_workflow.py")
    assert os.path.isfile(test_new_workflow_path), f"Test script {test_new_workflow_path} does not exist."
