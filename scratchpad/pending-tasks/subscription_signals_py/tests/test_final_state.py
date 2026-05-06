import os
import subprocess
import time
import pytest

PROJECT_DIR = "/home/user/subscription_app"

@pytest.fixture(scope="module")
def run_worker():
    worker_script = os.path.join(PROJECT_DIR, "worker.py")
    if not os.path.isfile(worker_script):
        pytest.fail(f"worker.py not found at {worker_script}")
        
    process = subprocess.Popen(
        ["python3", "worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    time.sleep(5) # Wait for worker to connect and start polling
    yield process
    
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_workflow_execution(run_worker):
    starter_script = os.path.join(PROJECT_DIR, "starter.py")
    assert os.path.isfile(starter_script), f"starter.py not found at {starter_script}"
    
    result = subprocess.run(
        ["python3", "starter.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    
    with open(os.path.join(PROJECT_DIR, "output.log"), "w") as f:
        f.write(result.stdout)
        if result.stderr:
            f.write("\n" + result.stderr)
            
    assert result.returncode == 0, f"starter.py failed with exit code {result.returncode}. Stderr: {result.stderr}"
    
    output_log_path = os.path.join(PROJECT_DIR, "output.log")
    assert os.path.isfile(output_log_path), f"{output_log_path} was not created."
