import httpx
from temporalio import activity

_HEADERS = {"User-Agent": "temporal-fetch-workflow/1.0"}


@activity.defn
async def fetch_data(url: str) -> str:
    """Perform a real HTTP GET and return the response body as text."""
    async with httpx.AsyncClient(headers=_HEADERS, follow_redirects=True) as client:
        response = await client.get(url)
        # Return body for all responses; the workflow gets the text regardless
        # of HTTP status so that transient upstream errors surface as a result
        # rather than an unhandled exception that causes the workflow to fail.
        return response.text
