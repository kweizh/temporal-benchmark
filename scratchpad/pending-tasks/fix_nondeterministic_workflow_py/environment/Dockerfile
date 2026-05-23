FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest python3-venv bash ripgrep && \
    pip3 install --break-system-packages pytest-json-ctrf temporalio && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Create the broken discount-py project that the executor must fix.
RUN mkdir -p /home/user/discount-py && \
    python3 -m venv /home/user/discount-py/.venv && \
    /home/user/discount-py/.venv/bin/pip install --upgrade pip && \
    /home/user/discount-py/.venv/bin/pip install "temporalio>=1.7,<2"

# workflows.py — intentionally non-deterministic. The executor must fix this.
RUN cat >/home/user/discount-py/workflows.py <<'EOF'
import datetime
import random
from temporalio import workflow


@workflow.defn(name="DiscountWorkflow")
class DiscountWorkflow:
    @workflow.run
    async def run(self, user_id: str) -> dict:
        # BUG: datetime.datetime.now() is non-deterministic inside a workflow.
        now = datetime.datetime.now()
        # BUG: random.choice() is non-deterministic inside a workflow.
        discount = random.choice([0, 5, 10, 15, 20])
        return {
            "user_id": user_id,
            "discount": discount,
            "decided_at": now.isoformat(),
        }
EOF

# activities.py — initially empty. The executor must define `pick_discount` here
# (or anywhere they prefer) and register it on the worker.
RUN cat >/home/user/discount-py/activities.py <<'EOF'
# Define your activities in this module. For example, an activity named
# `pick_discount` that returns one of [0, 5, 10, 15, 20].
EOF

# worker.py — registers the workflow but does NOT register any activity yet.
# The executor must update this file to register the new `pick_discount` Activity.
RUN cat >/home/user/discount-py/worker.py <<'EOF'
import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from workflows import DiscountWorkflow

TASK_QUEUE = "discount-py"


async def main():
    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[DiscountWorkflow],
        activities=[],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
EOF

# starter.py — runs the workflow and writes the result to output.log.
RUN cat >/home/user/discount-py/starter.py <<'EOF'
import asyncio
import json
import os

from temporalio.client import Client

TASK_QUEUE = "discount-py"
LOG_FILE = "/home/user/discount-py/output.log"


async def main():
    run_id = os.environ["ZEALT_RUN_ID"]
    workflow_id = f"discount-py-{run_id}"

    client = await Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )

    result = await client.execute_workflow(
        "DiscountWorkflow",
        "user-42",
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )

    with open(LOG_FILE, "w") as f:
        f.write(f"Workflow result: {json.dumps(result)}\n")

    print(f"Workflow result: {json.dumps(result)}")


if __name__ == "__main__":
    asyncio.run(main())
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="Temporal.io Python SDK environment with a deliberately non-deterministic DiscountWorkflow that the agent must fix and run against real Temporal Cloud."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest python3-venv bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - system temporalio installed via pip3 (used by tests/test_final_state.py)
#   - /home/user/discount-py: project directory
#   - /home/user/discount-py/.venv: project-local virtualenv with temporalio installed
#   - /home/user/discount-py/workflows.py: BROKEN, uses datetime.now() and random.choice()
#   - /home/user/discount-py/activities.py: empty stub for executor to define `pick_discount`
#   - /home/user/discount-py/worker.py: worker bootstrap (no activities registered yet)
#   - /home/user/discount-py/starter.py: starter that runs DiscountWorkflow and writes output.log
