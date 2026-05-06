import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/temporal-determinism"

def test_temporal_cli_available():
    assert shutil.which("temporal") is not None, "temporal CLI not found in PATH."

def test_python_available():
    assert shutil.which("python3") is not None, "python3 not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_workflow_file_exists():
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    assert os.path.isfile(workflow_path), f"Workflow file {workflow_path} does not exist."
    
    with open(workflow_path, "r") as f:
        content = f.read()
        assert "datetime.now()" in content, "Initial workflow.py should contain datetime.now()"
        assert "uuid.uuid4()" in content, "Initial workflow.py should contain uuid.uuid4()"
        assert "requests.get(" in content, "Initial workflow.py should contain requests.get("

def test_other_files_exist():
    for filename in ["activity.py", "worker.py", "server.py", "run_workflow.py", "requirements.txt"]:
        file_path = os.path.join(PROJECT_DIR, filename)
        assert os.path.isfile(file_path), f"File {file_path} does not exist."

def test_dependencies_installed():
    result = subprocess.run(["python3", "-c", "import temporalio; import requests"], capture_output=True)
    assert result.returncode == 0, "Required Python dependencies (temporalio, requests) are not installed."