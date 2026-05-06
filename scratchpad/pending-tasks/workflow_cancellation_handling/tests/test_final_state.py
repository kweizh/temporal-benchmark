import os
import subprocess
import time
import pytest
import signal

PROJECT_DIR = "/home/user/myproject"
CLEANUP_FILE = os.path.join(PROJECT_DIR, "cleanup_done.txt")

@pytest.fixture(scope="module")
def setup_and_run_worker():
    # npm install
    subprocess.run(["npm", "install"], cwd=PROJECT_DIR, check=True)
    # npx tsc
    subprocess.run(["npx", "tsc"], cwd=PROJECT_DIR, check=True)
    
    # Start worker
    process = subprocess.Popen(
        ["node", "dist/worker.js"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Wait for worker to initialize
    time.sleep(5)
    
    yield
    
    # Shut down worker
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_workflow_cancellation(setup_and_run_worker):
    # Remove cleanup file if it exists from previous runs
    if os.path.exists(CLEANUP_FILE):
        os.remove(CLEANUP_FILE)
        
    # Run client script
    result = subprocess.run(
        ["node", "dist/client.js"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Client script failed: {result.stderr}\n{result.stdout}"
    
    # Verify cleanup file
    assert os.path.isfile(CLEANUP_FILE), f"Cleanup file {CLEANUP_FILE} was not created."
    
    with open(CLEANUP_FILE, "r") as f:
        content = f.read().strip()
        
    assert "cleanup done" in content, f"Expected \"cleanup done\" in {CLEANUP_FILE}, got: {content}"
