FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio

RUN curl -sSf https://temporal.download/cli.sh | sh && \
    mv /root/.temporalio/bin/temporal /usr/local/bin/temporal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal Python SDK task environment for asynchronous activity completion."

RUN mkdir -p /home/user/project

# Container contents:
#   - temporalio installed for Python project.
#   - temporal CLI installed in /usr/local/bin.
#   - /home/user/project  — project directory for the task.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]