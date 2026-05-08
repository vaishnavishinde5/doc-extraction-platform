from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.document import DocumentType, ExtractionStatus


class ExtractionRequest(BaseModel):
    document_type: DocumentType
    output_fields: Optional[List[str]] = Field(
        default=None,
        description="Configurable list of fields to extract. If None, all template fields are extracted."
    )


class ExtractionResult(BaseModel):
    id: int
    filename: str
    document_type: DocumentType
    status: ExtractionStatus
    extracted_fields: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    total: int
    items: List[ExtractionResult]
