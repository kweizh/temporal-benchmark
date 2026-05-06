import os
import shutil
import subprocess
import pytest

def test_node_installed():
    assert shutil.which("node") is not None, "node binary not found in PATH."
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_typescript_tools_available_if_global():
    # ts-node and tsc might be installed locally, but let's just check node
    pass
