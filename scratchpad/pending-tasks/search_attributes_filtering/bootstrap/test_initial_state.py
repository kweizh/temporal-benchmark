import os
import shutil
import pytest

PROJECT_DIR = "/home/user/temporal-project"

def test_temporal_binary_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_python_binary_available():
    assert shutil.which("python") is not None, "python binary not found in PATH."

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_workflow_file_exists():
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    assert os.path.isfile(workflow_path), f"Workflow file {workflow_path} does not exist."

def test_worker_file_exists():
    worker_path = os.path.join(PROJECT_DIR, "worker.py")
    assert os.path.isfile(worker_path), f"Worker file {worker_path} does not exist."

def test_starter_file_exists():
    starter_path = os.path.join(PROJECT_DIR, "starter.py")
    assert os.path.isfile(starter_path), f"Starter file {starter_path} does not exist."
