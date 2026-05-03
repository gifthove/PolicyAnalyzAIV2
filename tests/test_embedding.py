from __future__ import annotations
from unittest.mock import MagicMock, call, patch

import pytest

from app.services.embedding_service import _BATCH_SIZE, get_embeddings


def _fake_response(texts: list[str], offset: int = 0):
    """Build a mock embeddings response matching the openai SDK shape."""
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(index=i, embedding=[0.1 * (offset + i)] * 3)
        for i in range(len(texts))
    ]
    return mock_response


@patch("app.services.embedding_service._client")
def test_empty_input_returns_empty_list(mock_client_fn):
    result = get_embeddings([])
    assert result == []
    mock_client_fn.assert_not_called()


@patch("app.services.embedding_service._client")
def test_single_text_returns_one_embedding(mock_client_fn):
    mock_client = MagicMock()
    mock_client_fn.return_value = mock_client
    mock_client.embeddings.create.return_value = _fake_response(["hello"])

    result = get_embeddings(["hello"])

    assert len(result) == 1
    assert isinstance(result[0], list)
    mock_client.embeddings.create.assert_called_once()


@patch("app.services.embedding_service._client")
def test_uses_deployment_name_from_config(mock_client_fn):
    import app.config as config

    mock_client = MagicMock()
    mock_client_fn.return_value = mock_client
    mock_client.embeddings.create.return_value = _fake_response(["text"])

    get_embeddings(["text"])

    _, kwargs = mock_client.embeddings.create.call_args
    assert kwargs["model"] == config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT


@patch("app.services.embedding_service._client")
def test_batches_large_input(mock_client_fn):
    mock_client = MagicMock()
    mock_client_fn.return_value = mock_client

    n = _BATCH_SIZE + 3
    texts = [f"text {i}" for i in range(n)]

    def side_effect(**kwargs):
        batch = kwargs["input"]
        return _fake_response(batch)

    mock_client.embeddings.create.side_effect = side_effect

    result = get_embeddings(texts)

    assert mock_client.embeddings.create.call_count == 2
    assert len(result) == n


@patch("app.services.embedding_service._client")
def test_result_order_matches_input_order(mock_client_fn):
    mock_client = MagicMock()
    mock_client_fn.return_value = mock_client

    # Return items in reversed index order to verify sorting is applied
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(index=2, embedding=[0.3, 0.3, 0.3]),
        MagicMock(index=0, embedding=[0.1, 0.1, 0.1]),
        MagicMock(index=1, embedding=[0.2, 0.2, 0.2]),
    ]
    mock_client.embeddings.create.return_value = mock_response

    result = get_embeddings(["a", "b", "c"])

    assert result[0] == [0.1, 0.1, 0.1]
    assert result[1] == [0.2, 0.2, 0.2]
    assert result[2] == [0.3, 0.3, 0.3]
