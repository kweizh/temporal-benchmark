import asyncio
import os
import sys
from temporalio import workflow
from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker

@workflow.defn
class StatefulWorkflow:
    def __init__(self) -> None:
        self.counter = 0
        self.stop = False

    @workflow.run
    async def run(self) -> int:
        for _ in range(10):
            if self.stop:
                break
            # Wait for 1 second or until stop is True
            await workflow.wait_condition(lambda: self.stop, timeout=1.0)
            if self.stop:
                break
            self.counter += 1
        return self.counter

    @workflow.query
    def get_counter(self) -> int:
        return self.counter

    @workflow.signal
    def finish(self) -> None:
        self.stop = True

async def main():
    api_key = os.environ.get("TEMPORAL_API_KEY")
    address = os.environ.get("TEMPORAL_ADDRESS")
    namespace = os.environ.get("TEMPORAL_NAMESPACE")
    run_id = os.environ.get("ZEALT_RUN_ID", "default-run-id")

    if not all([api_key, address, namespace]):
        print("Missing required environment variables.")
        sys.exit(1)

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=TLSConfig()
    )

    worker = Worker(
        client,
        task_queue="query-handler-py",
        workflows=[StatefulWorkflow],
    )

    # Start worker
    worker_task = asyncio.create_task(worker.run())

    try:
        # Start workflow
        handle = await client.start_workflow(
            StatefulWorkflow.run,
            id=f"query-wf-{run_id}",
            task_queue="query-handler-py",
        )

        # Wait until counter > 0 to ensure mid-flight query gets > 0
        mid_counter = 0
        for _ in range(15):
            await asyncio.sleep(1)
            try:
                mid_counter = await handle.query(StatefulWorkflow.get_counter)
                if mid_counter > 0:
                    break
            except Exception:
                pass
        
        print(f"Mid counter: {mid_counter}")

        # Send finish signal
        await handle.signal(StatefulWorkflow.finish)

        # Await final result
        final_counter = await handle.result()
        print(f"Final counter: {final_counter}")
    finally:
        # Shutdown worker
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
