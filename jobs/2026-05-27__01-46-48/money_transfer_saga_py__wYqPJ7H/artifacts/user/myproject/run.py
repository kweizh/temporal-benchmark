"""
Entrypoint: starts a Temporal Worker and executes the two saga workflow runs.

Usage:
    python3 /home/user/myproject/run.py

Environment variables required:
    TEMPORAL_ADDRESS   – Temporal Cloud gRPC endpoint (host:port)
    TEMPORAL_NAMESPACE – Temporal Cloud namespace
    TEMPORAL_API_KEY   – Temporal Cloud API key
    ZEALT_RUN_ID       – unique run identifier (used for task queue / workflow IDs)
"""
import asyncio
import logging
import os
import sys

# ── Make sure the project directory is on the Python path so that the
#    workflow and activity modules can be imported both by the worker
#    (which runs in the same process) and by Temporal's sandbox.
sys.path.insert(0, os.path.dirname(__file__))

from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.client import WorkflowFailureError

from activities import deposit, refund, withdraw
from workflow import MoneyTransferWorkflow

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_FILE = "/home/user/myproject/output.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s – %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("run")

# ── Configuration from environment ───────────────────────────────────────────
TEMPORAL_ADDRESS = os.environ["TEMPORAL_ADDRESS"]
TEMPORAL_NAMESPACE = os.environ["TEMPORAL_NAMESPACE"]
TEMPORAL_API_KEY = os.environ["TEMPORAL_API_KEY"]
ZEALT_RUN_ID = os.environ["ZEALT_RUN_ID"]

TASK_QUEUE = f"saga-py-{ZEALT_RUN_ID}"
WF_ID_OK = f"saga-ok-py-{ZEALT_RUN_ID}"
WF_ID_FAIL = f"saga-fail-py-{ZEALT_RUN_ID}"


async def main() -> None:
    logger.info("Connecting to Temporal Cloud at %s (namespace: %s)", TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE)

    client = await Client.connect(
        TEMPORAL_ADDRESS,
        namespace=TEMPORAL_NAMESPACE,
        api_key=TEMPORAL_API_KEY,
        tls=True,
    )

    # ── Start Worker as a background task ────────────────────────────────────
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[MoneyTransferWorkflow],
        activities=[withdraw, deposit, refund],
    )

    logger.info("Starting worker on task queue: %s", TASK_QUEUE)
    worker_task = asyncio.ensure_future(worker.run())

    # Give the worker a moment to connect and begin polling before we submit work.
    await asyncio.sleep(2)

    try:
        # ── Run 1: A -> B, amount 30 (expected: COMPLETED) ───────────────────
        logger.info("OK_WORKFLOW_ID: %s", WF_ID_OK)
        logger.info("Starting workflow run 1: %s", WF_ID_OK)

        result = await client.execute_workflow(
            MoneyTransferWorkflow.run,
            args=["A", "B", 30],
            id=WF_ID_OK,
            task_queue=TASK_QUEUE,
        )
        logger.info("Workflow %s completed with result: %s", WF_ID_OK, result)

        # ── Run 2: A -> B_FAIL, amount 50 (expected: FAILED after refund) ────
        logger.info("FAIL_WORKFLOW_ID: %s", WF_ID_FAIL)
        logger.info("Starting workflow run 2: %s", WF_ID_FAIL)

        try:
            await client.execute_workflow(
                MoneyTransferWorkflow.run,
                args=["A", "B_FAIL", 50],
                id=WF_ID_FAIL,
                task_queue=TASK_QUEUE,
            )
            logger.error("Workflow %s unexpectedly succeeded!", WF_ID_FAIL)
        except WorkflowFailureError as exc:
            logger.info(
                "Workflow %s failed as expected (saga compensation ran): %s",
                WF_ID_FAIL,
                exc,
            )

    finally:
        # ── Shut down worker ─────────────────────────────────────────────────
        logger.info("Shutting down worker…")
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
        logger.info("Worker stopped.")

    logger.info("All done. Final account state is in /workspace/accounts.json")


if __name__ == "__main__":
    asyncio.run(main())
