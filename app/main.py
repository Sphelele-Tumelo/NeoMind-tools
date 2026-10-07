import os

from fastapi import FastAPI, Query
from app.providers.searxng import SearXNGProvider


app = FastAPI(
    title="NeoMind Tools",
    version="0.1.0",
)

searxng = SearXNGProvider(
    base_url=os.getenv("SEARXNG_URL", "http://localhost:8080")
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "neomind-tools",
    }


@app.get("/tools/search")
async def search_web(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=10),
):
    results = await searxng.search(
        query=q,
        limit=limit,
    )

    return {
        "query": q,
        "results": results,
    }