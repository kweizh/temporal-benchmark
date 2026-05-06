import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/app"
ACTIVITY_FILE = os.path.join(PROJECT_DIR, "activity.py")

def test_activity_file_exists():
    assert os.path.isfile(ACTIVITY_FILE), f"activity.py not found at {ACTIVITY_FILE}"

def test_activity_fetch_data_returns_expected_result():
    test_script_content = """
import asyncio
from temporalio.testing import ActivityEnvironment
from activity import fetch_data

async def main():
    env = ActivityEnvironment()
    result = await env.run(fetch_data)
    assert isinstance(result, dict), "Result must be a dictionary"
    assert result.get("userId") == 1, f"Expected userId to be 1, got {result.get('userId')}"
    assert result.get("id") == 1, f"Expected id to be 1, got {result.get('id')}"
    print("SUCCESS")

if __name__ == "__main__":
    asyncio.run(main())
"""
    test_script_path = os.path.join(PROJECT_DIR, "test_activity_execution.py")
    with open(test_script_path, "w") as f:
        f.write(test_script_content)

    result = subprocess.run(
        ["python3", "test_activity_execution.py"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, f"Activity execution failed: {result.stderr}\n{result.stdout}"
    assert "SUCCESS" in result.stdout, f"Activity execution did not print SUCCESS. Output: {result.stdout}"
