import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/temporal-app"

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_package_json_exists():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), f"package.json not found at {package_json_path}"

def test_tsconfig_json_exists():
    tsconfig_path = os.path.join(PROJECT_DIR, "tsconfig.json")
    assert os.path.isfile(tsconfig_path), f"tsconfig.json not found at {tsconfig_path}"

def test_temporal_dependencies_installed():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json_path) as f:
        content = f.read()
    assert "@temporalio/client" in content, "Expected @temporalio/client in package.json"
    assert "@temporalio/worker" in content, "Expected @temporalio/worker in package.json"
    assert "@temporalio/workflow" in content, "Expected @temporalio/workflow in package.json"
    assert "@temporalio/activity" in content, "Expected @temporalio/activity in package.json"
    assert "@temporalio/envconfig" in content, "Expected @temporalio/envconfig in package.json"

def test_node_modules_exists():
    node_modules_path = os.path.join(PROJECT_DIR, "node_modules")
    assert os.path.isdir(node_modules_path), f"node_modules not found at {node_modules_path}"
