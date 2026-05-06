import os
import shutil
import subprocess
import pytest

def test_python_available():
    assert shutil.which("python") is not None, "python binary not found in PATH."

def test_temporal_cli_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."

def test_temporalio_installed():
    try:
        import temporalio
    except ImportError:
        pytest.fail("temporalio package is not installed.")

def test_temporal_server_running():
    # Check if temporal server is running by invoking cluster health or similar
    # or just check if port 7233 is open, but simple temporal CLI is better
    try:
        result = subprocess.run(
            ["temporal", "operator", "cluster", "health"],
            capture_output=True,
            text=True,
            check=True
        )
        assert "SERVE_STATUS_SERVING" in result.stdout or result.returncode == 0
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Temporal server does not appear to be running: {e.stderr}")
