FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages pytest-json-ctrf temporalio httpx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject

LABEL Author="generate-harbor-tasks"
LABEL Description="Temporal.io Python SDK task environment with the temporalio Python SDK and httpx pre-installed for the agent's HTTP GET activity workflow and the verifier."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - temporalio Python SDK installed via pip3 for both the agent's HTTP GET activity workflow implementation and the verifier
#   - httpx installed via pip3 so the agent can perform a real HTTP GET inside the Temporal Activity
#   - /home/user/myproject: empty project directory where the agent builds the Temporal Python app
