import os
import json
import shutil

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


def test_package_json_has_temporal_deps():
    pkg = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg) as f:
        data = json.load(f)
    deps = {}
    deps.update(data.get("dependencies", {}))
    deps.update(data.get("devDependencies", {}))
    for required in ("@temporalio/client", "@temporalio/worker", "@temporalio/workflow", "@temporalio/activity"):
        assert required in deps, f"Required dependency {required} missing from package.json."


def test_workflows_file_exists():
    p = os.path.join(PROJECT_DIR, "src", "workflows.ts")
    assert os.path.isfile(p), f"src/workflows.ts not found at {p}."


def test_activities_file_exists():
    p = os.path.join(PROJECT_DIR, "src", "activities.ts")
    assert os.path.isfile(p), f"src/activities.ts not found at {p}."


def test_worker_file_exists():
    p = os.path.join(PROJECT_DIR, "src", "worker.ts")
    assert os.path.isfile(p), f"src/worker.ts not found at {p}."


def test_client_file_exists():
    p = os.path.join(PROJECT_DIR, "src", "client.ts")
    assert os.path.isfile(p), f"src/client.ts not found at {p}."


def test_workflows_file_is_initially_broken():
    """The initial src/workflows.ts must contain the non-deterministic patterns
    (Math.random and new Date() ) that the agent is asked to remove."""
    p = os.path.join(PROJECT_DIR, "src", "workflows.ts")
    with open(p) as f:
        content = f.read()
    assert "Math.random" in content, (
        "Expected initial src/workflows.ts to contain 'Math.random' (the broken pattern)."
    )
    assert "new Date(" in content, (
        "Expected initial src/workflows.ts to contain 'new Date(' (the broken pattern)."
    )


def test_temporal_env_vars_present():
    for var in ("TEMPORAL_API_KEY", "TEMPORAL_ADDRESS", "TEMPORAL_NAMESPACE"):
        assert os.environ.get(var), f"Required environment variable {var} is not set."


def test_zealt_run_id_present():
    assert os.environ.get("ZEALT_RUN_ID"), "Required environment variable ZEALT_RUN_ID is not set."
