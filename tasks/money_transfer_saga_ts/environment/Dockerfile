FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf temporalio && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject
RUN mkdir -p /workspace && chmod 0777 /workspace && \
    printf '{"A": 100, "B": 0}' > /workspace/accounts.json && \
    chmod 0666 /workspace/accounts.json

LABEL Author="generate-harbor-tasks"
LABEL Description="Temporal.io TypeScript SDK saga task environment with Node.js v24 and the Python temporalio SDK for verification, including a pre-seeded /workspace/accounts.json with initial balances."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 for the Temporal TypeScript SDK saga task environment
#   - temporalio Python SDK installed via pip3 for verifying workflow execution in Temporal Cloud
#   - /home/user/myproject: empty project directory where the agent builds the Temporal TS saga app
#   - /workspace: writable directory containing accounts.json (seeded with {"A": 100, "B": 0})
