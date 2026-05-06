FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio

RUN mkdir -p /home/user/project && chmod 0755 /home/user/project

LABEL Author="any-task-builder"
LABEL Description="Temporal.io Python environment with temporalio installed and an empty project directory."

# Container contents:
#   - temporalio installed via pip.
#   - /home/user/project — empty directory for the user to create the Temporal workflow scripts.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
