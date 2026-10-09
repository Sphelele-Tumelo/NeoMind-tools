import asyncio

import httpx


class SearXNGUnavailableError(Exception):
    """Raised when SearXNG can't be reached or keeps failing after retries."""


class SearXNGProvider:
    # 502/503/504 from Render usually means the instance is waking up
    RETRYABLE_STATUS_CODES = {502, 503, 504}

    def __init__(
        self,
        base_url: str,
        max_retries: int = 3,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.timeout = timeout

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[dict]:

        params = {
            "q": query,
            "format": "json",
        }

        last_error: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(
                        f"{self.base_url}/search",
                        params=params,
                    )

                if response.status_code in self.RETRYABLE_STATUS_CODES:
                    last_error = RuntimeError(
                        f"SearXNG returned {response.status_code}"
                    )
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 * (attempt + 1))
                    continue

                # 403 and other errors are real config problems, so don't retry
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("results", [])[:limit]:
                    url = item.get("url")

                    if not isinstance(url, str) or not url.startswith(
                        ("https://", "http://")
                    ):
                        continue

                    results.append(
                        {
                            "title": item.get("title") or url,
                            "url": url,
                            "snippet": item.get("content") or "",
                            "source": item.get("engine"),
                            "published_at": item.get("published_at") or None,
                        }
                    )

                return results

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 * (attempt + 1))

        raise SearXNGUnavailableError(
            f"SearXNG unavailable after {self.max_retries} attempts: {last_error}"
        )