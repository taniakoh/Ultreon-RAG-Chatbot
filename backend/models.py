from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class SourceNode(BaseModel):
    document_name: str
    text: str
    score: float | None = None
    section: str | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceNode]
    confidence: str
