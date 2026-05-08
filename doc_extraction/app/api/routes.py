"""
FastAPI routes for the Document Extraction Platform.
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
import json

from app.db.database import get_db
from app.models.document import DocumentType
from app.schemas.document import ExtractionResult, DocumentListResponse
from app.services.extraction_service import DocumentExtractionService
from app.core.container import Container
from app.logging.aspect_logger import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/api/v1/documents", tags=["Document Extraction"])


def get_service() -> DocumentExtractionService:
    container = Container()
    return container.extraction_service()


@router.post("/extract", response_model=ExtractionResult, status_code=status.HTTP_201_CREATED)
async def extract_document(
    file: UploadFile = File(..., description="Image file (JPG/PNG/PDF) of the document"),
    document_type: DocumentType = Form(..., description="Type of document"),
    output_fields: Optional[str] = Form(
        default=None,
        description="Comma-separated list of fields to extract (optional)"
    ),
    db: Session = Depends(get_db),
    service: DocumentExtractionService = Depends(get_service),
):
    """
    Upload a document image and extract structured fields using OCR + LLM.
    """
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/jpg", "application/pdf"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not supported. Use JPG, PNG, or PDF.",
        )

    image_bytes = await file.read()

    # Parse configurable output fields
    fields_list: Optional[List[str]] = None
    if output_fields:
        fields_list = [f.strip() for f in output_fields.split(",") if f.strip()]

    log.info("extract_request_received", filename=file.filename, doc_type=document_type)

    doc = service.process_document(
        db=db,
        filename=file.filename,
        image_bytes=image_bytes,
        document_type=document_type,
        output_fields=fields_list,
    )

    return doc


@router.get("/", response_model=DocumentListResponse)
def list_documents(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    service: DocumentExtractionService = Depends(get_service),
):
    """List all extracted documents."""
    items = service.list_documents(db, skip=skip, limit=limit)
    total = service.count_documents(db)
    return DocumentListResponse(total=total, items=items)


@router.get("/{doc_id}", response_model=ExtractionResult)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    service: DocumentExtractionService = Depends(get_service),
):
    """Get a single document extraction result by ID."""
    doc = service.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc
