FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash tar gzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio==1.8.0

# Install Temporal CLI
RUN curl -sSf https://temporal.download/cli.sh | sh && \
    cp /root/.env/temporal/bin/temporal /usr/local/bin/temporal || true

# If the above fails or puts it somewhere else, let's just download the tarball
RUN if [ ! -f /usr/local/bin/temporal ]; then \
        curl -L "https://temporal.download/cli/archive/latest?platform=linux&arch=amd64" -o temporal.tar.gz && \
        tar -xzf temporal.tar.gz && \
        mv temporal /usr/local/bin/temporal && \
        rm temporal.tar.gz; \
    fi

RUN mkdir -p /home/user/retry_project && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal Python task environment for implementing a retry activity."

# Container contents:
#   - temporalio python package installed
#   - temporal CLI installed
#   - /home/user/retry_project - empty project directory

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]