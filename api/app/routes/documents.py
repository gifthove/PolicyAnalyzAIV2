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
from app.services.chunking_service import chunk_text
from app.services.document_service import SUPPORTED_TYPES, extract_text
from app.services.embedding_service import get_embeddings
from app.services.search_service import IndexedChunk, delete_document, index_chunks

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

    chunks = chunk_text(text)
    chunk_count = 0

    if chunks:
        try:
            embeddings = await asyncio.to_thread(get_embeddings, [c.text for c in chunks])
            now_iso = datetime.now(tz=timezone.utc).isoformat()
            indexed = [
                IndexedChunk(
                    id=f"{document_id}_{c.chunk_index}",
                    document_id=document_id,
                    source_name=source_name,
                    policy_date=str(policy_date) if policy_date else None,
                    chunk_index=c.chunk_index,
                    chunk_text=c.text,
                    embedding=embeddings[c.chunk_index],
                    created_at=now_iso,
                )
                for c in chunks
            ]
            chunk_count = await asyncio.to_thread(index_chunks, indexed)
        except Exception as exc:
            logger.error("Indexing failed: document_id=%s error=%s", document_id, exc)
            raise HTTPException(status_code=500, detail=f"Failed to index document chunks: {exc}")

    logger.info(
        "Document uploaded: document_id=%s words=%d chars=%d chunks=%d",
        document_id, word_count, char_count, chunk_count,
    )

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
        chunk_count=chunk_count,
    )


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["documents"],
)
async def delete_document_chunks(document_id: str) -> None:
    logger.info("Delete request received: document_id=%s", document_id)
    try:
        await asyncio.to_thread(delete_document, document_id)
    except Exception as exc:
        logger.error("Delete failed: document_id=%s error=%s", document_id, exc)
        raise HTTPException(status_code=500, detail=f"Failed to delete document chunks: {exc}")
