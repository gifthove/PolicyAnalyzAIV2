from __future__ import annotations

import logging

from openai import AzureOpenAI

import app.config as config
from app.services.search_service import RetrievedChunk

logger = logging.getLogger(__name__)

INSUFFICIENT_EVIDENCE_ANSWER = (
    "I don't have enough evidence in the retrieved policy documents to answer that question."
)

SYSTEM_PROMPT = """You are PolicyAnalyzAI, a careful policy analysis assistant.
Answer only from the provided retrieved context.
Every factual claim must be grounded in the context and cite the supporting chunk using bracketed citation numbers like [1].
If the context does not contain enough evidence, say you do not have enough evidence instead of guessing.
Do not use outside knowledge."""


def _client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_key=config.AZURE_OPENAI_KEY,
        api_version=config.AZURE_OPENAI_API_VERSION,
    )


def build_grounded_messages(question: str, chunks: list[RetrievedChunk]) -> list[dict[str, str]]:
    context_blocks = []
    for number, chunk in enumerate(chunks, start=1):
        source = chunk.source_name or "Unknown source"
        policy_date = chunk.policy_date or "Unknown date"
        context_blocks.append(
            "\n".join(
                [
                    f"[{number}]",
                    f"Source: {source}",
                    f"Document ID: {chunk.document_id}",
                    f"Chunk ID: {chunk.id}",
                    f"Chunk Index: {chunk.chunk_index}",
                    f"Policy Date: {policy_date}",
                    f"Text: {chunk.chunk_text}",
                ]
            )
        )

    context = "\n\n".join(context_blocks) if context_blocks else "No retrieved context."
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Retrieved context:\n"
                f"{context}\n\n"
                "User question:\n"
                f"{question}\n\n"
                "Write a concise grounded answer with citations. "
                "If the retrieved context is insufficient, say so plainly."
            ),
        },
    ]


def answer_question(question: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return INSUFFICIENT_EVIDENCE_ANSWER

    response = _client().chat.completions.create(
        model=config.AZURE_OPENAI_CHAT_DEPLOYMENT,
        messages=build_grounded_messages(question, chunks),
        temperature=0,
    )
    answer = (response.choices[0].message.content or "").strip()
    logger.info("Generated grounded answer using %d chunks", len(chunks))
    return answer or INSUFFICIENT_EVIDENCE_ANSWER
