FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages temporalio

RUN curl -sSf https://temporal.download/cli.sh | sh && mv ~/.temporalio/bin/temporal /usr/local/bin/temporal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal.io Python continue_as_new task environment."

RUN mkdir -p /home/user/project && \
    cd /home/user/project && \
    cat > workflow.py <<'EOF'
from datetime import timedelta
from temporalio import workflow

@workflow.defn
class ProcessItemsWorkflow:
    @workflow.run
    async def run(self, start_index: int, total_items: int) -> bool:
        processed_count = 0
        current_index = start_index

        while current_index < total_items:
            # Simulate processing an item
            await workflow.sleep(timedelta(milliseconds=1))
            processed_count += 1
            current_index += 1

        return True
EOF

# Container contents:
#   - python3, python3-pip, python3-pytest
#   - temporalio python SDK installed
#   - temporal CLI installed
#   - /home/user/project - Temporal project with workflow.py

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]