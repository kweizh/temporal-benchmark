import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/app"

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_temporalio_installed():
    result = subprocess.run(["python3", "-c", "import temporalio"], capture_output=True)
    assert result.returncode == 0, "temporalio Python package is not installed."
