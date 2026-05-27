import asyncio
import os

from temporalio.client import Client


async def main() -> None:
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    run_id = os.environ["ZEALT_RUN_ID"]

    workflow_id = f"loop-py-{run_id}"

    client = await Client.connect(
        address,
        namespace=namespace,
        tls=True,
        rpc_metadata={"temporal-namespace": namespace},
        api_key=api_key,
    )

    try:
        handle = client.get_workflow_handle(workflow_id)
        await handle.terminate(reason="Restarting with fixed workflow code")
        print(f"Terminated workflow '{workflow_id}'")
    except Exception as e:
        print(f"Could not terminate (may already be done): {e}")


if __name__ == "__main__":
    asyncio.run(main())
