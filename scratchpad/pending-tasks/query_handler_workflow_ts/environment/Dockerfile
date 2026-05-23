FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /workspace && chmod 0777 /workspace

RUN mkdir -p /home/user/myproject && \
    cd /home/user/myproject && \
    npm init -y >/dev/null 2>&1 && \
    npm install --silent --no-audit --no-fund --no-progress \
        @temporalio/client@^1.11.0 \
        @temporalio/worker@^1.11.0 \
        @temporalio/workflow@^1.11.0 \
        @temporalio/activity@^1.11.0 \
        typescript@^5.4.0 \
        ts-node@^10.9.0 \
        @types/node@^20.0.0

LABEL Author="generate-harbor-tasks"
LABEL Description="Temporal.io TypeScript SDK task environment for implementing a query-handler workflow against Temporal Cloud."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 for the Temporal TypeScript SDK
#   - /home/user/myproject: scaffolded Node.js project with @temporalio/{client,worker,workflow,activity}, typescript, ts-node
#   - /workspace: writable scratch directory used by the task for progress.log and progress.json
