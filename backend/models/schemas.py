from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    query: str


class ExplanationCard(BaseModel):
    title: str
    modern_trigger: str
    ancestral_mechanism: str
    brain_chemistry: str
    the_insight: str
    confidence: str  # "high" | "medium" | "low"
    sources: list[str]


class ExplainResponse(BaseModel):
    explanation: ExplanationCard
    retrieval_ms: int
    chunks_used: int
