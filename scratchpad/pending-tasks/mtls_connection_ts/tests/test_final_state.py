import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/temporal-app"
CONFIG_FILE = os.path.join(PROJECT_DIR, "config.toml")
CONNECT_SCRIPT = os.path.join(PROJECT_DIR, "connect.ts")

def test_config_file_exists():
    """Priority 3 fallback: basic file existence check."""
    assert os.path.isfile(CONFIG_FILE), f"config.toml not found at {CONFIG_FILE}"

def test_cli_reads_cert_path():
    """Priority 1: Use Temporal CLI to verify the TLS client_cert_path in the config."""
    env = os.environ.copy()
    env["TEMPORAL_CONFIG_FILE"] = CONFIG_FILE
    
    result = subprocess.run(
        ["temporal", "--profile", "prod", "config", "get", "tls.client_cert_path"],
        capture_output=True, text=True, cwd=PROJECT_DIR, env=env
    )
    assert result.returncode == 0, f"'temporal config get tls.client_cert_path' failed: {result.stderr}"
    
    output = result.stdout.strip()
    assert "/home/user/temporal-app/certs/client.pem" in output, \
        f"Expected cert path to be '/home/user/temporal-app/certs/client.pem', got: {output}"

def test_cli_reads_key_path():
    """Priority 1: Use Temporal CLI to verify the TLS client_key_path in the config."""
    env = os.environ.copy()
    env["TEMPORAL_CONFIG_FILE"] = CONFIG_FILE
    
    result = subprocess.run(
        ["temporal", "--profile", "prod", "config", "get", "tls.client_key_path"],
        capture_output=True, text=True, cwd=PROJECT_DIR, env=env
    )
    assert result.returncode == 0, f"'temporal config get tls.client_key_path' failed: {result.stderr}"
    
    output = result.stdout.strip()
    assert "/home/user/temporal-app/certs/client.key" in output, \
        f"Expected key path to be '/home/user/temporal-app/certs/client.key', got: {output}"

def test_connect_script_executes_and_handles_error():
    """Priority 1: Run the TypeScript script and verify it attempts the connection and catches the error."""
    assert os.path.isfile(CONNECT_SCRIPT), f"connect.ts not found at {CONNECT_SCRIPT}"
    
    result = subprocess.run(
        ["npx", "tsx", "connect.ts"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    
    # The script should catch the connection error and exit gracefully (code 0)
    assert result.returncode == 0, \
        f"connect.ts execution failed with code {result.returncode}.\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    
    output = result.stdout.lower() + result.stderr.lower()
    
    # Verify that the script caught the error and printed the expected message
    # "connection failed as expected" or similar indication of error handling
    assert "connection failed as expected" in output or "failed to connect" in output, \
        f"Expected error handling message in output, got: {result.stdout}\n{result.stderr}"
