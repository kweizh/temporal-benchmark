FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages --ignore-installed \
        pytest-json-ctrf \
        pytest-asyncio \
        temporalio && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject && chmod 0755 /home/user/myproject
RUN mkdir -p /workspace && chmod 0777 /workspace

LABEL Author="generate-harbor-tasks"
LABEL Description="Temporal.io Python SDK environment for the retry_policy_fixed_py task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - temporalio Python SDK for connecting to Temporal Cloud
#   - pytest-asyncio for asynchronous tests in tests/test_final_state.py
#   - /home/user/myproject: project directory for the agent's solution
#   - /workspace: writable directory used for attempts.log and result.log output
