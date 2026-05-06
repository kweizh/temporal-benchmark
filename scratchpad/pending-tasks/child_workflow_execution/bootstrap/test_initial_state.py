import os
import shutil
import pytest

def test_temporal_cli_available():
    assert shutil.which("temporal") is not None, "temporal CLI not found in PATH."
