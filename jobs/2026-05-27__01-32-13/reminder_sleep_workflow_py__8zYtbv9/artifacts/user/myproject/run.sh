#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --quiet temporalio

python3 /home/user/myproject/main.py
