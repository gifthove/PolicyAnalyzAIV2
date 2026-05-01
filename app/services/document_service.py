from __future__ import annotations
import io
from typing import Tuple

SUPPORTED_TYPES: dict[str, str] = {
    "pdf":  "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt":  "text/plain",
}


def extract_text(file_bytes: bytes, extension: str) -> Tuple[str, int, int]:
    """Returns (text, word_count, char_count). Raises ValueError for unsupported extensions."""
    if extension == "pdf":
        text = _extract_pdf(file_bytes)
    elif extension == "docx":
        text = _extract_docx(file_bytes)
    elif extension == "txt":
        text = _extract_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported extension: {extension}")
    words = len(text.split()) if text.strip() else 0
    return text, words, len(text)


def _extract_pdf(file_bytes: bytes) -> str:
    from PyPDF2 import PdfReader
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx(file_bytes: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)


def _extract_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="replace")
