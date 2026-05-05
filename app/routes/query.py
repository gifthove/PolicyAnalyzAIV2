from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException

from app.schemas.query import QueryCitation, QueryRequest, QueryResponse
from app.services.embedding_service import get_embeddings
from app.services.language_model_service import answer_question
from app.services.search_service import retrieve_chunks

logger = logging.getLogger(__name__)

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest) -> QueryResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Question must not be blank")

    try:
        embeddings = await asyncio.to_thread(get_embeddings, [question])
        chunks = await asyncio.to_thread(retrieve_chunks, embeddings[0], request.top_k)
        answer = await asyncio.to_thread(answer_question, question, chunks)
    except Exception as exc:
        logger.error("Query failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to answer query: {exc}")

    citations = [
        QueryCitation(
            citation_id=index,
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            source_name=chunk.source_name,
            policy_date=chunk.policy_date,
            chunk_index=chunk.chunk_index,
            score=chunk.score,
            text=chunk.chunk_text,
        )
        for index, chunk in enumerate(chunks, start=1)
    ]

    return QueryResponse(answer=answer, citations=citations)
