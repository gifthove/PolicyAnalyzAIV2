from __future__ import annotations
from unittest.mock import MagicMock, patch

import pytest

from app.services.search_service import (
    IndexedChunk,
    delete_document,
    ensure_index_exists,
    index_chunks,
    retrieve_chunks,
)


def _make_chunk(doc_id: str = "doc-1", idx: int = 0) -> IndexedChunk:
    return IndexedChunk(
        id=f"{doc_id}_{idx}",
        document_id=doc_id,
        source_name="Test Policy",
        policy_date="2024-01-15",
        chunk_index=idx,
        chunk_text="Some policy text.",
        embedding=[0.1] * 3,
        created_at="2026-01-01T00:00:00+00:00",
    )


@patch("app.services.search_service._index_client")
def test_ensure_index_exists_calls_create_or_update(mock_client_fn):
    mock_client = MagicMock()
    mock_client_fn.return_value = mock_client

    ensure_index_exists()

    mock_client.create_or_update_index.assert_called_once()
    index_arg = mock_client.create_or_update_index.call_args[0][0]
    assert index_arg.name is not None


@patch("app.services.search_service._index_client")
def test_ensure_index_uses_configured_dimensions(mock_client_fn):
    import app.config as config

    mock_client = MagicMock()
    mock_client_fn.return_value = mock_client

    ensure_index_exists()

    index_arg = mock_client.create_or_update_index.call_args[0][0]
    vector_field = next(f for f in index_arg.fields if f.name == "embedding")
    assert vector_field.vector_search_dimensions == config.AZURE_OPENAI_EMBEDDING_DIMENSIONS


@patch("app.services.search_service._search_client")
def test_index_chunks_returns_succeeded_count(mock_client_fn):
    mock_client = MagicMock()
    mock_client_fn.return_value = mock_client

    mock_result = [MagicMock(succeeded=True), MagicMock(succeeded=True)]
    mock_client.upload_documents.return_value = mock_result

    count = index_chunks([_make_chunk(idx=0), _make_chunk(idx=1)])

    assert count == 2
    mock_client.upload_documents.assert_called_once()


@patch("app.services.search_service._search_client")
def test_index_chunks_empty_input_returns_zero(mock_client_fn):
    count = index_chunks([])
    assert count == 0
    mock_client_fn.assert_not_called()


@patch("app.services.search_service._search_client")
def test_index_chunks_partial_failure_counts_only_succeeded(mock_client_fn):
    mock_client = MagicMock()
    mock_client_fn.return_value = mock_client

    mock_client.upload_documents.return_value = [
        MagicMock(succeeded=True),
        MagicMock(succeeded=False),
    ]

    count = index_chunks([_make_chunk(idx=0), _make_chunk(idx=1)])

    assert count == 1


@patch("app.services.search_service._search_client")
def test_delete_document_removes_all_chunks(mock_client_fn):
    mock_client = MagicMock()
    mock_client_fn.return_value = mock_client

    mock_client.search.return_value = [{"id": "doc-1_0"}, {"id": "doc-1_1"}]

    delete_document("doc-1")

    mock_client.delete_documents.assert_called_once_with(
        documents=[{"id": "doc-1_0"}, {"id": "doc-1_1"}]
    )


@patch("app.services.search_service._search_client")
def test_delete_document_no_chunks_skips_delete(mock_client_fn):
    mock_client = MagicMock()
    mock_client_fn.return_value = mock_client
    mock_client.search.return_value = []

    delete_document("doc-999")

    mock_client.delete_documents.assert_not_called()


@patch("app.services.search_service._search_client")
def test_retrieve_chunks_uses_vector_query(mock_client_fn):
    mock_client = MagicMock()
    mock_client_fn.return_value = mock_client
    mock_client.search.return_value = [
        {
            "id": "doc-1_0",
            "document_id": "doc-1",
            "source_name": "Policy A",
            "policy_date": "2024-01-15",
            "chunk_index": 0,
            "chunk_text": "Relevant policy text.",
            "@search.score": 0.91,
        }
    ]

    chunks = retrieve_chunks([0.1, 0.2, 0.3], top_k=3)

    assert len(chunks) == 1
    assert chunks[0].id == "doc-1_0"
    assert chunks[0].score == 0.91
    _, kwargs = mock_client.search.call_args
    assert kwargs["top"] == 3
    assert kwargs["vector_queries"][0].as_dict()["fields"] == "embedding"
    assert kwargs["vector_queries"][0].as_dict()["k"] == 3


@patch("app.services.search_service._search_client")
def test_retrieve_chunks_empty_embedding_returns_empty(mock_client_fn):
    assert retrieve_chunks([]) == []
    mock_client_fn.assert_not_called()
