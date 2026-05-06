FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends nodejs && \
    cd /tmp && \
    wget -qO temporal_cli.tar.gz "https://temporal.download/cli/archive/latest?platform=linux&arch=amd64" && \
    tar -xzf temporal_cli.tar.gz && \
    mv temporal /usr/local/bin/temporal && \
    rm -rf /tmp/temporal_cli.tar.gz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Task environment for configuring a Temporal Client with mTLS in TypeScript. Includes Node.js and Temporal CLI."

# Container contents:
#   - always required libs: curl ca-certificates git python3 python3-pip python3-pytest bash
#   - Node.js v22
#   - Temporal CLI installed to /usr/local/bin/temporal
#   - /home/user: base directory for the project

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
