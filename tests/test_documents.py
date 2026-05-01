from __future__ import annotations
import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

FAKE_BLOB_URL = "https://fake.blob.core.windows.net/documents/test-id/file.txt"


def _mock_blob_client():
    mock_blob_svc = MagicMock()
    mock_blob_instance = mock_blob_svc.from_connection_string.return_value
    mock_blob_client_instance = mock_blob_instance.get_blob_client.return_value
    mock_blob_client_instance.url = FAKE_BLOB_URL
    mock_blob_client_instance.upload_blob.return_value = None
    return mock_blob_svc


def _make_minimal_pdf() -> bytes:
    from PyPDF2 import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def _make_minimal_docx() -> bytes:
    from docx import Document
    doc = Document()
    doc.add_paragraph("Policy content here.")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@patch("app.services.blob_service.BlobServiceClient", new_callable=_mock_blob_client)
def test_upload_txt_happy_path(mock_blob):
    response = client.post(
        "/documents",
        files={"file": ("policy.txt", b"This is a sample policy document.", "text/plain")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["file_type"] == "txt"
    assert data["status"] == "uploaded"
    assert data["word_count"] > 0
    assert data["char_count"] > 0
    assert data["filename"] == "policy.txt"
    assert "document_id" in data
    assert "upload_timestamp" in data


@patch("app.services.blob_service.BlobServiceClient", new_callable=_mock_blob_client)
def test_upload_pdf_happy_path(mock_blob):
    pdf_bytes = _make_minimal_pdf()
    response = client.post(
        "/documents",
        files={"file": ("report.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 201
    assert response.json()["file_type"] == "pdf"


@patch("app.services.blob_service.BlobServiceClient", new_callable=_mock_blob_client)
def test_upload_docx_happy_path(mock_blob):
    docx_bytes = _make_minimal_docx()
    response = client.post(
        "/documents",
        files={"file": ("brief.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert response.status_code == 201
    assert response.json()["file_type"] == "docx"


@patch("app.services.blob_service.BlobServiceClient", new_callable=_mock_blob_client)
def test_upload_with_metadata(mock_blob):
    response = client.post(
        "/documents",
        files={"file": ("gdpr.txt", b"General Data Protection Regulation text.", "text/plain")},
        data={"source_name": "GDPR Policy", "policy_date": "2024-01-15"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["source_name"] == "GDPR Policy"
    assert data["policy_date"] == "2024-01-15"


def test_unsupported_file_type():
    response = client.post(
        "/documents",
        files={"file": ("data.xlsx", b"fake excel content", "application/vnd.ms-excel")},
    )
    assert response.status_code == 400
    assert "Unsupported" in response.json()["detail"]


@patch("app.services.blob_service.BlobServiceClient", new_callable=_mock_blob_client)
def test_file_too_large(mock_blob):
    large_content = b"x" * (21 * 1024 * 1024)
    response = client.post(
        "/documents",
        files={"file": ("big.txt", large_content, "text/plain")},
    )
    assert response.status_code == 413
    assert "20 MB" in response.json()["detail"]


@patch("app.services.blob_service.BlobServiceClient")
def test_blob_storage_failure(mock_blob_class):
    mock_instance = mock_blob_class.from_connection_string.return_value
    mock_instance.get_blob_client.return_value.upload_blob.side_effect = Exception("Azure error")

    response = client.post(
        "/documents",
        files={"file": ("policy.txt", b"Some content.", "text/plain")},
    )
    assert response.status_code == 500
    assert "blob storage" in response.json()["detail"]
