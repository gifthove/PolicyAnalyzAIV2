from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question to answer from indexed policy chunks")
    top_k: int = Field(5, ge=1, le=20, description="Number of relevant chunks to retrieve")


class QueryCitation(BaseModel):
    citation_id: int
    chunk_id: str
    document_id: str
    source_name: Optional[str] = None
    policy_date: Optional[str] = None
    chunk_index: int
    score: Optional[float] = None
    text: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[QueryCitation]
