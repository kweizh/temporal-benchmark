import os
import shutil
import pytest

PROJECT_DIR = "/home/user/project"

def test_node_installed():
    assert shutil.which("node") is not None, "node binary not found in PATH."
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_temporal_env_vars_set():
    assert "TEMPORAL_API_KEY" in os.environ, "TEMPORAL_API_KEY environment variable is not set."
    assert "TEMPORAL_ADDRESS" in os.environ, "TEMPORAL_ADDRESS environment variable is not set."
    assert "TEMPORAL_NAMESPACE" in os.environ, "TEMPORAL_NAMESPACE environment variable is not set."