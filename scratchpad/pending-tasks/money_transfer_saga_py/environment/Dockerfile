FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages pytest-json-ctrf temporalio && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/myproject && chmod 0755 /home/user/myproject

RUN mkdir -p /workspace && \
    printf '%s\n' '{"A": 100, "B": 0}' > /workspace/accounts.json && \
    chmod 0644 /workspace/accounts.json

LABEL Author="generate-harbor-tasks"
LABEL Description="Temporal.io Python SDK money-transfer saga task environment connected to Temporal Cloud."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - temporalio Python SDK for building Temporal workers, workflows, and activities
#   - /home/user/myproject: working directory where the agent implements the saga
#   - /workspace/accounts.json: initial account-balance state ({"A": 100, "B": 0}) for the saga activities
