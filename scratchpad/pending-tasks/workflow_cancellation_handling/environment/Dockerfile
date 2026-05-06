FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash wget && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSf https://temporal.download/cli.sh | sh && \
    cp /root/.temporalio/bin/temporal /usr/local/bin/temporal

RUN mkdir -p /home/user/myproject && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal TypeScript task environment with Node.js and Temporal CLI."

# Container contents:
#   - Node.js v24 installed
#   - Temporal CLI installed
#   - /home/user/myproject - empty directory for the project

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
