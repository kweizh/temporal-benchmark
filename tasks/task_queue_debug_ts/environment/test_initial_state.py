import json
import os
import shutil

import pytest

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


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


def test_workflows_file_exists():
    wf = os.path.join(PROJECT_DIR, "src", "workflows.ts")
    assert os.path.isfile(wf), f"Workflows source file {wf} does not exist."


def test_initial_worker_uses_task_queue_b():
    worker = os.path.join(PROJECT_DIR, "src", "worker.ts")
    with open(worker) as f:
        content = f.read()
    assert "task-queue-B" in content, (
        "Initial state: src/worker.ts is expected to register Task Queue 'task-queue-B' "
        "so the agent can discover the mismatch with the client."
    )


def test_initial_client_uses_task_queue_a():
    client = os.path.join(PROJECT_DIR, "src", "client.ts")
    with open(client) as f:
        content = f.read()
    assert "task-queue-A" in content, (
        "Initial state: src/client.ts is expected to start the workflow on Task Queue 'task-queue-A' "
        "so the agent can discover the mismatch with the worker."
    )


def test_temporal_env_vars_present():
    for var in ("TEMPORAL_API_KEY", "TEMPORAL_ADDRESS", "TEMPORAL_NAMESPACE"):
        assert os.environ.get(var), f"Environment variable {var} must be set."


def test_zealt_run_id_present():
    assert os.environ.get("ZEALT_RUN_ID"), "Environment variable ZEALT_RUN_ID must be set."
