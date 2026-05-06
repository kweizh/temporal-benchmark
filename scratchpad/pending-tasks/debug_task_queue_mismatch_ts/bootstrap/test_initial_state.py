import os
import shutil
import pytest

PROJECT_DIR = "/home/user/project"

def test_temporal_binary_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_source_files_exist():
    for file in ["src/client.ts", "src/worker.ts", "src/workflows.ts"]:
        file_path = os.path.join(PROJECT_DIR, file)
        assert os.path.isfile(file_path), f"Source file {file_path} does not exist."
