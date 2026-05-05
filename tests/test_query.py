from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.search_service import RetrievedChunk

client = TestClient(app)


def _chunk() -> RetrievedChunk:
    return RetrievedChunk(
        id="doc-1_0",
        document_id="doc-1",
        source_name="Policy A",
        policy_date="2024-01-15",
        chunk_index=0,
        chunk_text="Staff must complete annual privacy training.",
        score=0.91,
    )


@patch("app.routes.query.answer_question", return_value="Staff must complete annual privacy training [1].")
@patch("app.routes.query.retrieve_chunks", return_value=[_chunk()])
@patch("app.routes.query.get_embeddings", return_value=[[0.1, 0.2, 0.3]])
def test_query_happy_path(mock_embeddings, mock_retrieve, mock_answer):
    response = client.post("/query", json={"question": "What training is required?", "top_k": 3})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Staff must complete annual privacy training [1]."
    assert data["citations"][0]["citation_id"] == 1
    assert data["citations"][0]["chunk_id"] == "doc-1_0"
    assert data["citations"][0]["text"] == "Staff must complete annual privacy training."
    mock_embeddings.assert_called_once_with(["What training is required?"])
    mock_retrieve.assert_called_once_with([0.1, 0.2, 0.3], 3)
    mock_answer.assert_called_once()


@patch(
    "app.routes.query.answer_question",
    return_value="I don't have enough evidence in the retrieved policy documents to answer that question.",
)
@patch("app.routes.query.retrieve_chunks", return_value=[])
@patch("app.routes.query.get_embeddings", return_value=[[0.1, 0.2, 0.3]])
def test_query_no_retrieved_chunks_returns_no_citations(mock_embeddings, mock_retrieve, mock_answer):
    response = client.post("/query", json={"question": "What is the lunch menu?"})

    assert response.status_code == 200
    data = response.json()
    assert "don't have enough evidence" in data["answer"]
    assert data["citations"] == []


def test_query_blank_question_rejected():
    response = client.post("/query", json={"question": "   "})

    assert response.status_code == 422
