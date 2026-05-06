import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/app"

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_temporalio_installed():
    result = subprocess.run(["python3", "-c", "import temporalio"], capture_output=True)
    assert result.returncode == 0, "temporalio is not installed in the environment."

def test_aiohttp_installed():
    result = subprocess.run(["python3", "-c", "import aiohttp"], capture_output=True)
    assert result.returncode == 0, "aiohttp is not installed in the environment."
