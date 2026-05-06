import os
import subprocess
import time
import pytest

PROJECT_DIR = "/home/user/temporal-app"

@pytest.fixture(scope="module")
def start_worker():
    # Start the worker
    process = subprocess.Popen(
        ["npx", "ts-node", "src/worker.ts"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Wait for the worker to connect
    time.sleep(10)
    
    yield
    
    # Shut down the worker
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_client_execution(start_worker):
    """Priority 1: Run the client script and verify output."""
    result = subprocess.run(
        ["npx", "ts-node", "src/client.ts"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, \
        f"Client script failed to execute: {result.stderr}"
    assert "delectus aut autem" in result.stdout, \
        f"Expected 'delectus aut autem' in stdout, got: {result.stdout}"

def test_source_files_exist():
    """Priority 3 fallback: basic file existence checks."""
    assert os.path.isfile(os.path.join(PROJECT_DIR, "src/activities.ts")), "src/activities.ts not found"
    assert os.path.isfile(os.path.join(PROJECT_DIR, "src/workflows.ts")), "src/workflows.ts not found"
    assert os.path.isfile(os.path.join(PROJECT_DIR, "src/worker.ts")), "src/worker.ts not found"
    assert os.path.isfile(os.path.join(PROJECT_DIR, "src/client.ts")), "src/client.ts not found"
