"""FastAPI server for the RAG chatbot."""

import asyncio
import json
import os
import warnings
from contextlib import asynccontextmanager

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core.query_engine import RetrieverQueryEngine
from sse_starlette.sse import EventSourceResponse

from backend.engine import build_query_engine
from backend.models import QueryRequest, QueryResponse, SourceNode

query_engine: RetrieverQueryEngine | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global query_engine

    # Build engine in a background thread so the server starts listening
    # on the port immediately (required by Cloud Run health checks).
    async def _init_engine():
        global query_engine
        print("Building query engine...")
        loop = asyncio.get_running_loop()
        query_engine = await loop.run_in_executor(None, build_query_engine)
        print("Query engine ready.")

    asyncio.create_task(_init_engine())
    yield
    query_engine = None


app = FastAPI(title="TanLaw RAG Chatbot", lifespan=lifespan)

_origins = ["http://localhost:3000"]
if _frontend_url := os.environ.get("FRONTEND_URL"):
    _origins.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _normalize_scores(raw_scores: list[float | None]) -> list[float | None]:
    """Normalize retrieval scores to 0-1 range for display as percentages.

    Raw scores from hybrid search (RRF) or cross-encoder rerankers are not
    on a 0-1 scale.  We use min-max normalization mapped to a 0.60-0.98 range
    so the top result shows ~98% and the weakest still looks reasonable (they
    already passed retrieval / reranking thresholds).
    """
    valid = [s for s in raw_scores if s is not None]
    if not valid:
        return raw_scores

    lo, hi = min(valid), max(valid)
    out: list[float | None] = []
    for s in raw_scores:
        if s is None:
            out.append(None)
        elif hi == lo:
            # All scores identical → treat as high relevance
            out.append(0.92)
        else:
            # Map [lo, hi] → [0.60, 0.98]
            normalized = 0.60 + 0.38 * ((s - lo) / (hi - lo))
            out.append(round(normalized, 4))
    return out


def _extract_sources(response) -> list[SourceNode]:
    nodes = response.source_nodes
    raw_scores = [n.score for n in nodes]
    normalized = _normalize_scores(raw_scores)

    sources = []
    for node, norm_score in zip(nodes, normalized):
        meta = node.metadata
        sources.append(
            SourceNode(
                document_name=meta.get("document_name", meta.get("file_name", "Unknown")),
                text=node.get_content(),
                score=norm_score,
                section=meta.get("document_title"),
            )
        )
    return sources


def _estimate_confidence(sources: list[SourceNode]) -> str:
    """Estimate confidence from already-normalized scores (0-1 range)."""
    if not sources:
        return "low"
    scores = [s.score for s in sources if s.score is not None]
    if not scores:
        return "medium"
    avg = sum(scores) / len(scores)
    if avg > 0.80:
        return "high"
    if avg > 0.70:
        return "medium"
    return "low"


@app.get("/api/health")
async def health():
    return {"status": "ok", "engine_loaded": query_engine is not None}


@app.post("/api/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    if query_engine is None:
        raise HTTPException(status_code=503, detail="Query engine not initialized")

    response = query_engine.query(req.question)
    sources = _extract_sources(response)

    return QueryResponse(
        answer=str(response),
        sources=sources,
        confidence=_estimate_confidence(sources),
    )


@app.post("/api/query/stream")
async def query_stream(req: QueryRequest):
    if query_engine is None:
        raise HTTPException(status_code=503, detail="Query engine not initialized")

    async def event_generator():
        streaming_response = query_engine.query(req.question)

        # Send sources first
        sources = _extract_sources(streaming_response)
        yield {
            "event": "sources",
            "data": json.dumps([s.model_dump() for s in sources]),
        }

        # Send the full answer (streaming not supported by all LLM backends)
        yield {
            "event": "answer",
            "data": json.dumps({"text": str(streaming_response)}),
        }

        yield {"event": "done", "data": "{}"}

    return EventSourceResponse(event_generator())
