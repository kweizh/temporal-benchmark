/**
 * activities.ts
 *
 * Activities are the correct place for all I/O (network calls, file system, etc.)
 * because they run in a normal Node.js context and are retried by Temporal on failure.
 * The workflow code itself must remain deterministic and must never perform I/O directly.
 */

/**
 * Performs a real HTTP GET request to the given URL and returns the response body
 * as a plain string. Uses the global `fetch` available in Node 18+.
 */
export async function fetchData(url: string): Promise<string> {
  const response = await fetch(url, {
    headers: {
      // GitHub API requires a User-Agent header
      'User-Agent': 'temporal-fetch-url-workflow/1.0',
    },
  });

  if (!response.ok) {
    throw new Error(
      `HTTP request failed: ${response.status} ${response.statusText} for URL ${url}`
    );
  }

  return await response.text();
}
