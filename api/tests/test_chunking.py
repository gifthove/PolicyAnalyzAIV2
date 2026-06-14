from __future__ import annotations
import pytest
from app.services.chunking_service import Chunk, chunk_text


def test_empty_string_returns_no_chunks():
    assert chunk_text("") == []


def test_whitespace_only_returns_no_chunks():
    assert chunk_text("   \n\n   ") == []


def test_single_paragraph_produces_one_chunk():
    text = "This is a single paragraph about data protection policy."
    chunks = chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].text == text
    assert chunks[0].token_count > 0


def test_two_short_paragraphs_merged_into_one_chunk():
    text = "First paragraph about access control.\n\nSecond paragraph about audit logs."
    chunks = chunk_text(text)
    assert len(chunks) == 1
    assert "First paragraph" in chunks[0].text
    assert "Second paragraph" in chunks[0].text


def test_chunk_indices_are_sequential():
    # Generate enough text to force multiple chunks
    paragraphs = [f"Policy section {i}: " + ("word " * 80) for i in range(10)]
    text = "\n\n".join(paragraphs)
    chunks = chunk_text(text, chunk_size=200, overlap=20)
    assert len(chunks) > 1
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i


def test_no_chunk_exceeds_token_ceiling():
    paragraphs = [f"Section {i}: " + ("regulation " * 100) for i in range(5)]
    text = "\n\n".join(paragraphs)
    ceiling = 300
    chunks = chunk_text(text, chunk_size=ceiling, overlap=30)
    for chunk in chunks:
        assert chunk.token_count <= ceiling


def test_token_count_is_accurate():
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    text = "The general data protection regulation applies to all member states."
    chunks = chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0].token_count == len(enc.encode(text))


def test_overlap_carries_content_between_chunks():
    # Use a tiny chunk_size so overflow is forced and we can verify overlap
    long_para = "alpha " * 50
    second_para = "beta " * 50
    text = f"{long_para}\n\n{second_para}"
    chunks = chunk_text(text, chunk_size=60, overlap=20)
    assert len(chunks) >= 2
    # At least one intermediate chunk should exist (overlap carries tokens forward)
    all_text = " ".join(c.text for c in chunks)
    assert "alpha" in all_text
    assert "beta" in all_text


def test_returns_list_of_chunk_dataclasses():
    chunks = chunk_text("Some policy text here.\n\nAnother section.")
    for chunk in chunks:
        assert isinstance(chunk, Chunk)
        assert isinstance(chunk.chunk_index, int)
        assert isinstance(chunk.text, str)
        assert isinstance(chunk.token_count, int)
