FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Temporal CLI
RUN curl -sSf https://temporal.download/cli.sh | sh && \
    cp /root/.temporalio/bin/temporal /usr/local/bin/temporal

# Install temporalio Python SDK
RUN pip3 install --break-system-packages temporalio

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal environment with Python SDK and local dev server."

# Initialize the project directory
RUN mkdir -p /home/user/project

# Container contents:
#   - python3, pip, pytest, curl, git
#   - temporal cli installed at /usr/local/bin/temporal
#   - temporalio python sdk installed
#   - /home/user/project initialized

CMD ["/bin/bash", "-c", "temporal server start-dev --ip 0.0.0.0 --ui-ip 0.0.0.0 & sleep 5 && trap : TERM INT; sleep infinity & wait"]