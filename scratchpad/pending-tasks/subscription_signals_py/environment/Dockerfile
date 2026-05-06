FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal Python SDK environment for Subscription Workflow task."

RUN mkdir -p /home/user/subscription_app && \
    chmod 0755 /home/user/subscription_app

# Container contents:
#   - temporalio installed for Python.
#   - /home/user/subscription_app - empty directory for the project

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
