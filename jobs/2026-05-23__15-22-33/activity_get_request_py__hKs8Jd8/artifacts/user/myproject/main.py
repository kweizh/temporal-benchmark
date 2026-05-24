import asyncio
import os
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
import httpx

# Activity definition
@activity.defn(name="fetch_repo_full_name")
async def fetch_repo_full_name(owner: str, repo: str) -> str:
    # GitHub API requires a User-Agent header
    headers = {"User-Agent": "Temporal-Activity-Python"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["full_name"]

# Workflow definition
@workflow.defn(name="FetchRepoWorkflow")
class FetchRepoWorkflow:
    @workflow.run
    async def run(self, owner: str, repo: str) -> str:
        return await workflow.execute_activity(
            fetch_repo_full_name,
            args=[owner, repo],
            start_to_close_timeout=timedelta(seconds=30),
        )

async def main():
    # Read environment variables
    temporal_address = os.environ.get("TEMPORAL_ADDRESS")
    temporal_namespace = os.environ.get("TEMPORAL_NAMESPACE")
    temporal_api_key = os.environ.get("TEMPORAL_API_KEY")
    zealt_run_id = os.environ.get("ZEALT_RUN_ID")

    if not all([temporal_address, temporal_namespace, temporal_api_key, zealt_run_id]):
        # Fallback for debugging if needed, but requirements say do not hard-code
        missing = [v for v in ["TEMPORAL_ADDRESS", "TEMPORAL_NAMESPACE", "TEMPORAL_API_KEY", "ZEALT_RUN_ID"] if not os.environ.get(v)]
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    # Connect to Temporal Cloud
    client = await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=True,
    )

    # Run worker and client together
    task_queue = "repo-fetch-py"
    
    # Start the worker
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[FetchRepoWorkflow],
        activities=[fetch_repo_full_name],
    )
    
    # Run the worker in the background and execute the workflow
    async with worker:
        # Execute workflow
        result = await client.execute_workflow(
            FetchRepoWorkflow.run,
            args=["temporalio", "temporal"],
            id=f"repo-fetch-py-{zealt_run_id}",
            task_queue=task_queue,
        )
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
