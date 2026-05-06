FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSf https://temporal.download/cli.sh | sh

RUN pip3 install --break-system-packages temporalio

RUN mkdir -p /home/user/temporal-project && chmod -R 0755 /home/user

ENV PATH="/root/.temporalio/bin:${PATH}"

LABEL Author="any-task-builder"
LABEL Description="Temporal child workflow task environment with Temporal CLI and Python SDK installed."

# Container contents:
#   - Temporal CLI installed
#   - Python temporalio SDK installed
#   - /home/user/temporal-project - empty directory for the project

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
