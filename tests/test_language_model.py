from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.services.language_model_service import (
    INSUFFICIENT_EVIDENCE_ANSWER,
    answer_question,
    build_grounded_messages,
)
from app.services.search_service import RetrievedChunk


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


def test_build_grounded_messages_contains_context_and_rules():
    messages = build_grounded_messages("What training is required?", [_chunk()])

    assert messages[0]["role"] == "system"
    assert "Answer only from the provided retrieved context" in messages[0]["content"]
    assert "Staff must complete annual privacy training." in messages[1]["content"]
    assert "What training is required?" in messages[1]["content"]


def test_answer_question_without_chunks_returns_insufficient_evidence():
    assert answer_question("What training is required?", []) == INSUFFICIENT_EVIDENCE_ANSWER


@patch("app.services.language_model_service._client")
def test_answer_question_calls_chat_model(mock_client_fn):
    mock_client = MagicMock()
    mock_client_fn.return_value = mock_client
    mock_choice = MagicMock()
    mock_choice.message.content = "Staff must complete annual privacy training [1]."
    mock_client.chat.completions.create.return_value.choices = [mock_choice]

    answer = answer_question("What training is required?", [_chunk()])

    assert answer == "Staff must complete annual privacy training [1]."
    mock_client.chat.completions.create.assert_called_once()
    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["temperature"] == 0
