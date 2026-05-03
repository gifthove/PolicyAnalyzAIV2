from __future__ import annotations
import re
from dataclasses import dataclass

import tiktoken

_ENCODING_NAME = "cl100k_base"
_encoder: tiktoken.Encoding | None = None


def _get_encoder() -> tiktoken.Encoding:
    global _encoder
    if _encoder is None:
        _encoder = tiktoken.get_encoding(_ENCODING_NAME)
    return _encoder


def _token_count(text: str) -> int:
    return len(_get_encoder().encode(text))


def _split_by_tokens(text: str, chunk_size: int, overlap: int) -> list[str]:
    enc = _get_encoder()
    tokens = enc.encode(text)
    results: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        results.append(enc.decode(tokens[start:end]))
        if end == len(tokens):
            break
        start = end - overlap
    return results


def _trailing_overlap(parts: list[str], overlap_tokens: int) -> list[str]:
    result: list[str] = []
    total = 0
    for part in reversed(parts):
        t = _token_count(part)
        if total + t <= overlap_tokens:
            result.insert(0, part)
            total += t
        else:
            break
    return result


@dataclass
class Chunk:
    chunk_index: int
    text: str
    token_count: int


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[Chunk]:
    """Split text into overlapping chunks using paragraph boundaries and a token ceiling."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    raw_chunks: list[str] = []
    buffer: list[str] = []
    buffer_tokens = 0

    for para in paragraphs:
        para_tokens = _token_count(para)

        if para_tokens > chunk_size:
            if buffer:
                raw_chunks.append("\n\n".join(buffer))
                buffer = []
                buffer_tokens = 0
            for sub in _split_by_tokens(para, chunk_size, overlap):
                raw_chunks.append(sub)
        elif buffer_tokens + para_tokens > chunk_size and buffer:
            raw_chunks.append("\n\n".join(buffer))
            overlap_parts = _trailing_overlap(buffer, overlap)
            buffer = overlap_parts + [para]
            buffer_tokens = sum(_token_count(p) for p in buffer)
        else:
            buffer.append(para)
            buffer_tokens += para_tokens

    if buffer:
        raw_chunks.append("\n\n".join(buffer))

    return [
        Chunk(chunk_index=i, text=c, token_count=_token_count(c))
        for i, c in enumerate(raw_chunks)
        if c.strip()
    ]
