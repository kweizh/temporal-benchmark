FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user/project && chmod 0755 /home/user/project

LABEL Author="any-task-builder"
LABEL Description="Node.js 24 environment with an empty project directory for Temporal TypeScript development."

# Container contents:
#   - Node.js v24 installed.
#   - /home/user/project — empty directory for the task.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]