FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSf https://temporal.download/cli.sh | sh && \
    mv /root/.temporalio/bin/temporal /usr/local/bin/temporal

RUN pip3 install --break-system-packages temporalio pytest-asyncio

RUN mkdir -p /home/user/subscription && chmod 0755 /home/user/subscription

LABEL Author="any-task-builder"
LABEL Description="Temporal environment for Python SDK with temporal server running locally."

# Container contents:
#   - python3, pip, pytest, pytest-asyncio
#   - temporal CLI in /usr/local/bin
#   - temporalio Python SDK
#   - /home/user/subscription project directory

CMD ["/bin/bash", "-c", "temporal server start-dev --ip 0.0.0.0 & trap : TERM INT; sleep infinity & wait"]
