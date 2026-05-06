import os
import subprocess
import json
import pytest

PROJECT_DIR = "/home/user/temporal-project"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")

def test_search_attribute_registered():
    """Priority 1: Use Temporal CLI to verify the search attribute is registered."""
    result = subprocess.run(
        ["temporal", "operator", "search-attribute", "list", "--output", "json"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"'temporal operator search-attribute list' failed: {result.stderr}"
    
    # The output format is JSON, something like {"customAttributes": {"CustomStatus": "INDEXED_VALUE_TYPE_KEYWORD"}}
    try:
        attrs = json.loads(result.stdout)
        custom_attrs = attrs.get("customAttributes", {})
        assert "CustomStatus" in custom_attrs, f"Search attribute 'CustomStatus' not found. Found: {list(custom_attrs.keys())}"
        assert custom_attrs["CustomStatus"] == "INDEXED_VALUE_TYPE_KEYWORD", f"Expected 'CustomStatus' to be 'INDEXED_VALUE_TYPE_KEYWORD', got {custom_attrs['CustomStatus']}"
    except json.JSONDecodeError:
        pytest.fail(f"Failed to parse JSON output from temporal cli: {result.stdout}")

def test_output_log_exists_and_contains_count():
    """Priority 3: Check the log file."""
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist."
    with open(LOG_FILE, "r") as f:
        content = f.read()
    assert "Count:" in content or "count:" in content.lower() or content.strip().isdigit(), \
        f"Expected {LOG_FILE} to contain a count output, got: {content}"

def test_workflow_count_via_cli():
    """Priority 1: Use Temporal CLI to count workflows matching the query."""
    result = subprocess.run(
        ["temporal", "workflow", "count", "--query", "CustomStatus='Completed'"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"'temporal workflow count' failed: {result.stderr}"
    
    # The output is something like "Count: 1"
    output = result.stdout.strip()
    assert "Count: 0" not in output, f"Expected count > 0, got: {output}"
    assert "Count:" in output or output.isdigit(), f"Unexpected output format from count command: {output}"
