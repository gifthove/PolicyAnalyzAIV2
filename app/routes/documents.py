from __future__ import annotations
import asyncio
import logging
import uuid
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.config import AZURE_BLOB_CONTAINER
from app.schemas.document import DocumentUploadResponse
from app.services.blob_service import upload_blob
from app.services.document_service import SUPPORTED_TYPES, extract_text

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_FILE_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post(
    "/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["documents"],
)
async def upload_document(
    file: UploadFile = File(...),
    source_name: Optional[str] = Form(None),
    policy_date: Optional[date] = Form(None),
) -> DocumentUploadResponse:
    logger.info("Upload request received: filename=%s", file.filename)

    parts = (file.filename or "").rsplit(".", 1)
    ext = parts[-1].lower() if len(parts) == 2 else ""
    if ext not in SUPPORTED_TYPES:
        logger.warning("Rejected unsupported file type: filename=%s", file.filename)
        raise HTTPException(status_code=400, detail="Unsupported file type. Accepted: pdf, docx, txt")

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_BYTES:
        logger.warning("Rejected oversized file: filename=%s size=%d", file.filename, len(file_bytes))
        raise HTTPException(status_code=413, detail="File exceeds 20 MB limit")

    try:
        text, word_count, char_count = extract_text(file_bytes, ext)
    except ValueError as exc:
        logger.warning("Text extraction failed: filename=%s error=%s", file.filename, exc)
        raise HTTPException(status_code=400, detail=str(exc))

    document_id = str(uuid.uuid4())
    blob_path = f"{document_id}/{file.filename}"

    try:
        await asyncio.to_thread(
            upload_blob, AZURE_BLOB_CONTAINER, blob_path, file_bytes, SUPPORTED_TYPES[ext]
        )
    except Exception as exc:
        logger.error("Blob upload failed: document_id=%s blob_path=%s error=%s", document_id, blob_path, exc)
        raise HTTPException(status_code=500, detail=f"Failed to upload to blob storage: {exc}")

    logger.info("Document uploaded: document_id=%s words=%d chars=%d", document_id, word_count, char_count)

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename or "",
        file_type=ext,
        size_bytes=len(file_bytes),
        upload_timestamp=datetime.now(tz=timezone.utc),
        source_name=source_name,
        policy_date=policy_date,
        blob_path=blob_path,
        word_count=word_count,
        char_count=char_count,
    )
