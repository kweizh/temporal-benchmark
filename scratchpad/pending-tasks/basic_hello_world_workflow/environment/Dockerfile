FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio

RUN curl -sSf https://temporal.download/cli.sh | sh && \
    mv ~/.temporalio/bin/temporal /usr/local/bin/temporal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal Hello World task environment with Python SDK and Temporal CLI."

RUN mkdir -p /home/user/project

# Container contents:
#   - python3, python3-pip, temporalio
#   - temporal CLI installed to /usr/local/bin/temporal
#   - /home/user/project - directory for the task

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]