"""FastAPI server for the RAG chatbot."""

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
    print("Building query engine...")
    query_engine = build_query_engine()
    print("Query engine ready.")
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


def _extract_sources(response) -> list[SourceNode]:
    sources = []
    for node in response.source_nodes:
        meta = node.metadata
        sources.append(
            SourceNode(
                document_name=meta.get("document_name", meta.get("file_name", "Unknown")),
                text=node.get_content(),
                score=node.score,
                section=meta.get("document_title"),
            )
        )
    return sources


def _estimate_confidence(response) -> str:
    if not response.source_nodes:
        return "low"
    scores = [n.score for n in response.source_nodes if n.score is not None]
    if not scores:
        return "medium"
    avg = sum(scores) / len(scores)
    if avg > 0.75:
        return "high"
    if avg > 0.5:
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

    return QueryResponse(
        answer=str(response),
        sources=_extract_sources(response),
        confidence=_estimate_confidence(response),
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
