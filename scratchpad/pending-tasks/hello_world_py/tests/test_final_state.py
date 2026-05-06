import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/temporal-hello"
MAIN_FILE = os.path.join(PROJECT_DIR, "main.py")
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")

def test_main_file_exists():
    assert os.path.isfile(MAIN_FILE), f"The script {MAIN_FILE} does not exist."

def test_main_script_execution():
    # Run the script and write output to output.log
    with open(LOG_FILE, "w") as f:
        result = subprocess.run(
            ["python3", "main.py"],
            cwd=PROJECT_DIR,
            stdout=f,
            stderr=subprocess.PIPE,
            text=True
        )
    
    assert result.returncode == 0, f"Script execution failed with error:\n{result.stderr}"

def test_output_log_contains_hello_world():
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} was not created."
    with open(LOG_FILE, "r") as f:
        content = f.read()
    assert "Hello, World!" in content, f"Expected 'Hello, World!' in output.log, got:\n{content}"
