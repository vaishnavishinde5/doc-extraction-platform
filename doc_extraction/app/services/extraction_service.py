"""
DocumentExtractionService: the main orchestrator.
Follows Single Responsibility + Dependency Inversion principles.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentType, ExtractionStatus
from app.extractors.ocr_extractor import BaseOCRExtractor
from app.extractors.llm_extractor import LLMExtractor
from app.templates.document_templates import get_template
from app.logging.aspect_logger import log_aspect, get_logger

log = get_logger(__name__)


class DocumentExtractionService:
    """
    Orchestrates the end-to-end pipeline:
    1. Save document record (PENDING)
    2. OCR → raw text
    3. LLM → structured fields
    4. Save extracted fields (SUCCESS / FAILED)
    """

    def __init__(self, ocr_extractor: BaseOCRExtractor, llm_extractor: LLMExtractor):
        self._ocr = ocr_extractor
        self._llm = llm_extractor

    @log_aspect
    def process_document(
        self,
        db: Session,
        filename: str,
        image_bytes: bytes,
        document_type: DocumentType,
        output_fields: Optional[List[str]] = None,
    ) -> Document:
        # 1. Create DB record
        doc = Document(
            filename=filename,
            document_type=document_type,
            status=ExtractionStatus.PROCESSING,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        try:
            # 2. OCR
            log.info("ocr_start", doc_id=doc.id, filename=filename)
            raw_text = self._ocr.extract_text(image_bytes)
            doc.raw_ocr_text = raw_text

            # 3. Template lookup
            template = get_template(document_type.value)

            # 4. LLM extraction
            log.info("llm_start", doc_id=doc.id)
            extracted = self._llm.extract_fields(raw_text, template, output_fields)

            # 5. Update record with results
            doc.extracted_fields = extracted
            doc.status = ExtractionStatus.SUCCESS
            log.info("extraction_complete", doc_id=doc.id, status="success")

        except Exception as exc:
            log.error("extraction_failed", doc_id=doc.id, error=str(exc))
            doc.status = ExtractionStatus.FAILED
            doc.error_message = str(exc)

        db.commit()
        db.refresh(doc)
        return doc

    @log_aspect
    def get_document(self, db: Session, doc_id: int) -> Optional[Document]:
        return db.query(Document).filter(Document.id == doc_id).first()

    @log_aspect
    def list_documents(self, db: Session, skip: int = 0, limit: int = 50) -> List[Document]:
        return db.query(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    @log_aspect
    def count_documents(self, db: Session) -> int:
        return db.query(Document).count()
