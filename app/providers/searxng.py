import httpx


class SearXNGProvider:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def search(self, query: str, limit: int = 5) -> list[dict]:
        params = {
            "q": query,
            "format": "json",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.base_url}/search",
                params=params,
            )

            response.raise_for_status()

        data = response.json()

        results = []

        for result in data.get("results", [])[:limit]:
            results.append(
                {
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "snippet": result.get("content"),
                }
            )

        return results