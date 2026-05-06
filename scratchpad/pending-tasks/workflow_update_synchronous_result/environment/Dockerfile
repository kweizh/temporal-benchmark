FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSf https://temporal.download/cli.sh | sh && \
    mv /root/.temporalio/bin/temporal /usr/local/bin/temporal

RUN pip3 install --break-system-packages temporalio

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal task environment with Temporal CLI and Python SDK installed."

# Container contents:
#   - always required libs: curl wget ca-certificates git python3 python3-pip python3-pytest bash
#   - temporal CLI
#   - temporalio Python SDK
#   - /home/user: base directory for the project

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]