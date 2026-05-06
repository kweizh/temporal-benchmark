FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio

RUN curl -sSf https://temporal.download/cli.sh | sh && \
    cp /root/.temporalio/bin/temporal /usr/local/bin/temporal

RUN mkdir -p /home/user/temporal_project && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal Python SDK environment with temporal CLI installed."

# Container contents:
#   - python3, pip3, pytest
#   - temporalio Python SDK installed
#   - temporal CLI installed
#   - /home/user/temporal_project directory created

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]