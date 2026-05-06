import os
import shutil
import subprocess
import pytest

def test_python_available():
    assert shutil.which("python") is not None or shutil.which("python3") is not None, "Python binary not found in PATH."

def test_pip_available():
    assert shutil.which("pip") is not None or shutil.which("pip3") is not None, "pip binary not found in PATH."

def test_temporal_cli_available():
    assert shutil.which("temporal") is not None, "temporal binary not found in PATH."
