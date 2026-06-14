from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="UUID v4 identifier for this document")
    filename: str
    file_type: str
    size_bytes: int
    upload_timestamp: datetime
    source_name: Optional[str] = None
    policy_date: Optional[date] = None
    blob_path: str
    word_count: int
    char_count: int
    chunk_count: int = 0
    status: str = "uploaded"
