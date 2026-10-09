import os

from fastapi import FastAPI, HTTPException, Query
from app.providers.searxng import SearXNGProvider, SearXNGUnavailableError


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
    try:
        results = await searxng.search(
            query=q,
            limit=limit,
        )
    except SearXNGUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="Web search is temporarily unavailable.",
        )

    return {
        "query": q,
        "results": results,
    }