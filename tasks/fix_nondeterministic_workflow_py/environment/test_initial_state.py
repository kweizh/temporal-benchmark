import os
import re
import subprocess

PROJECT_DIR = "/home/user/discount-py"
VENV_PYTHON = os.path.join(PROJECT_DIR, ".venv", "bin", "python")


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_venv_python_exists():
    assert os.path.isfile(VENV_PYTHON), f"Virtualenv Python {VENV_PYTHON} does not exist."


def test_temporalio_importable():
    result = subprocess.run(
        [VENV_PYTHON, "-c", "import temporalio; print(temporalio.__name__)"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"temporalio is not importable in the project venv. stderr: {result.stderr}"
    )


def test_workflows_file_exists():
    workflows_path = os.path.join(PROJECT_DIR, "workflows.py")
    assert os.path.isfile(workflows_path), f"{workflows_path} does not exist."


def test_workflows_file_is_initially_broken():
    """The initial workflows.py must contain the non-deterministic constructs that
    the executor needs to fix. This ensures the executor actually makes the change."""
    workflows_path = os.path.join(PROJECT_DIR, "workflows.py")
    with open(workflows_path) as f:
        content = f.read()
    assert re.search(r"datetime\.datetime\.now|datetime\.now", content), (
        "Initial workflows.py should contain a non-deterministic datetime.now() call."
    )
    assert re.search(r"random\.choice", content), (
        "Initial workflows.py should contain a non-deterministic random.choice() call."
    )


def test_worker_file_exists():
    worker_path = os.path.join(PROJECT_DIR, "worker.py")
    assert os.path.isfile(worker_path), f"{worker_path} does not exist."


def test_starter_file_exists():
    starter_path = os.path.join(PROJECT_DIR, "starter.py")
    assert os.path.isfile(starter_path), f"{starter_path} does not exist."


def test_temporal_env_vars_set():
    for var in ("TEMPORAL_ADDRESS", "TEMPORAL_NAMESPACE", "TEMPORAL_API_KEY", "ZEALT_RUN_ID"):
        assert os.environ.get(var), f"Environment variable {var} is not set."
