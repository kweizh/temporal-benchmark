import os
import shutil
import pytest

PROJECT_DIR = "/home/user/project"

def test_python_binary_available():
    assert shutil.which("python") is not None, "python binary not found in PATH."

def test_temporal_binary_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."
