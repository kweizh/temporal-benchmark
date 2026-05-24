import json
import os
import shutil

import pytest

PROJECT_DIR = "/home/user/myproject"
WORKSPACE_DIR = "/workspace"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_workspace_dir_exists():
    assert os.path.isdir(WORKSPACE_DIR), (
        f"Workspace directory {WORKSPACE_DIR} (for attempts.log) does not exist."
    )


def test_attempts_log_not_yet_created():
    log_path = os.path.join(WORKSPACE_DIR, "attempts.log")
    assert not os.path.exists(log_path), (
        f"Attempts log {log_path} should not exist before the task runs."
    )


def test_package_json_exists():
    pkg = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(pkg), f"package.json not found at {pkg}."


def test_package_json_declares_temporal_sdk():
    pkg = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg) as f:
        data = json.load(f)
    deps = {}
    deps.update(data.get("dependencies", {}))
    deps.update(data.get("devDependencies", {}))
    for required in (
        "@temporalio/client",
        "@temporalio/worker",
        "@temporalio/workflow",
        "@temporalio/activity",
    ):
        assert required in deps, f"package.json must declare dependency {required}."


def test_node_modules_installed():
    nm = os.path.join(PROJECT_DIR, "node_modules", "@temporalio", "worker")
    assert os.path.isdir(nm), "Expected @temporalio/worker to be installed in node_modules."


def test_worker_file_exists():
    worker = os.path.join(PROJECT_DIR, "src", "worker.ts")
    assert os.path.isfile(worker), f"Worker source file {worker} does not exist."


def test_client_file_exists():
    client = os.path.join(PROJECT_DIR, "src", "client.ts")
    assert os.path.isfile(client), f"Client source file {client} does not exist."


def test_temporal_env_vars_present():
    for var in ("TEMPORAL_API_KEY", "TEMPORAL_ADDRESS", "TEMPORAL_NAMESPACE"):
        assert os.environ.get(var), f"Environment variable {var} must be set."


def test_zealt_run_id_present():
    assert os.environ.get("ZEALT_RUN_ID"), "Environment variable ZEALT_RUN_ID must be set."
