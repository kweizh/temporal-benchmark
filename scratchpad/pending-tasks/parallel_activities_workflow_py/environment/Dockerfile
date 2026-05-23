FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    ln -sf /usr/bin/python3 /usr/local/bin/python && \
    pip3 install --break-system-packages pytest-json-ctrf temporalio httpx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject

LABEL Author="generate-harbor-tasks"
LABEL Description="Temporal.io Python SDK task environment with the temporalio and httpx Python packages preinstalled for parallel-activities workflow."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - temporalio Python SDK installed via pip3 for both the agent's task code and the verifier (used to fetch workflow handle and history)
#   - httpx installed via pip3 for the activity's parallel GET requests
#   - /usr/local/bin/python symlink to python3 so `python main.py` works out of the box
#   - /home/user/myproject: empty project directory where the agent builds the Temporal Python app
