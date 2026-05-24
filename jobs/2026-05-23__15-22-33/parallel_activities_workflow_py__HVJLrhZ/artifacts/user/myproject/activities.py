import httpx
from temporalio import activity

@activity.defn
async def fetch_url(url: str) -> int:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.status_code
