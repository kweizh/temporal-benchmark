import shutil
import pytest

def test_temporal_cli_available():
    assert shutil.which("temporal") is not None, "Temporal CLI binary not found in PATH."

def test_node_available():
    assert shutil.which("node") is not None, "Node.js binary not found in PATH."

def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."
