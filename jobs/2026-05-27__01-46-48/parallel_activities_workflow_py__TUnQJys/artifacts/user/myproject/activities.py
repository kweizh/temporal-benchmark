"""Temporal activities — safe to use any I/O library here."""

import httpx
from temporalio import activity


@activity.defn
async def fetch_url(url: str) -> int:
    """Issue GET <url> and return the HTTP status code as int."""
    headers = {
        # GitHub API requires Accept header to respond with 200 instead of 403.
        "Accept": "application/vnd.github+json",
        "User-Agent": "temporal-parallel-fetch/1.0",
    }
    async with httpx.AsyncClient(
        follow_redirects=True, timeout=20.0, headers=headers
    ) as client:
        response = await client.get(url)
        return int(response.status_code)
