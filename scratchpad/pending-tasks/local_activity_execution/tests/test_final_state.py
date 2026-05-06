import os
import pytest

PROJECT_DIR = "/home/user/project"

def test_main_py_exists_and_uses_local_activity():
    main_py_path = os.path.join(PROJECT_DIR, "main.py")
    assert os.path.isfile(main_py_path), f"{main_py_path} does not exist."
    
    with open(main_py_path, "r") as f:
        content = f.read()
    
    assert "execute_local_activity" in content, "main.py does not use execute_local_activity."

def test_output_log_contains_expected_result():
    output_log_path = os.path.join(PROJECT_DIR, "output.log")
    assert os.path.isfile(output_log_path), f"Log file {output_log_path} does not exist. Did the script run successfully?"
    
    with open(output_log_path, "r") as f:
        content = f.read()
    
    assert "Hello, Temporal!" in content, f"Expected 'Hello, Temporal!' in {output_log_path}, got: {content}"
