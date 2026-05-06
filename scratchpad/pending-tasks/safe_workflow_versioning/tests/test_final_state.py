import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"

def test_pytest_passes():
    """Priority 1: Run the provided pytest suite to verify determinism and new behavior."""
    result = subprocess.run(
        ["pytest", "test_workflow.py"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR
    )
    assert result.returncode == 0, f"pytest test_workflow.py failed:\n{result.stdout}\n{result.stderr}"
