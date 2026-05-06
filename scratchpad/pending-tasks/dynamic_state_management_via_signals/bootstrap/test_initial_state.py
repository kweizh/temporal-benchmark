import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/myproject"

def test_temporal_cli_binary_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."
