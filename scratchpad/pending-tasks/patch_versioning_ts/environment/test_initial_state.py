import os
import shutil
import json
import pytest

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_package_json_exists():
    path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(path), f"package.json missing at {path}."


def test_package_json_has_temporal_deps():
    path = os.path.join(PROJECT_DIR, "package.json")
    with open(path) as f:
        pkg = json.load(f)
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    for required in [
        "@temporalio/client",
        "@temporalio/worker",
        "@temporalio/workflow",
        "@temporalio/activity",
    ]:
        assert required in deps, f"{required} must be declared in package.json dependencies."


def test_workflows_ts_exists_and_has_orderworkflow():
    path = os.path.join(PROJECT_DIR, "src", "workflows.ts")
    assert os.path.isfile(path), f"src/workflows.ts missing at {path}."
    with open(path) as f:
        content = f.read()
    assert "OrderWorkflow" in content, "OrderWorkflow must be declared in src/workflows.ts initially."
    assert "chargeCard" in content, "chargeCard activity reference must exist in src/workflows.ts initially."
    assert "shipOrder" in content, "shipOrder activity reference must exist in src/workflows.ts initially."
    # The agent has not yet added the patch.
    assert "add-notify-customer" not in content, (
        "src/workflows.ts must NOT already include the 'add-notify-customer' patch before the task starts."
    )


def test_activities_ts_exists_and_declares_notify():
    path = os.path.join(PROJECT_DIR, "src", "activities.ts")
    assert os.path.isfile(path), f"src/activities.ts missing at {path}."
    with open(path) as f:
        content = f.read()
    for name in ["chargeCard", "shipOrder", "notifyCustomer"]:
        assert name in content, f"Activity '{name}' must be declared in src/activities.ts initially."


def test_worker_ts_exists():
    path = os.path.join(PROJECT_DIR, "src", "worker.ts")
    assert os.path.isfile(path), f"src/worker.ts missing at {path}."


def test_node_modules_installed():
    # Dependencies should be pre-installed in the image.
    nm = os.path.join(PROJECT_DIR, "node_modules", "@temporalio", "worker")
    assert os.path.isdir(nm), f"@temporalio/worker not installed under {nm}."


def test_temporal_env_vars_present():
    for var in ["TEMPORAL_API_KEY", "TEMPORAL_ADDRESS", "TEMPORAL_NAMESPACE"]:
        assert os.environ.get(var), f"Environment variable {var} must be set."


def test_zealt_run_id_present():
    assert os.environ.get("ZEALT_RUN_ID"), "ZEALT_RUN_ID environment variable must be set."
