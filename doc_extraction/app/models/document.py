from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, Text, Enum
from sqlalchemy.sql import func
import enum

from app.db.database import Base


class DocumentType(str, enum.Enum):
    AADHAAR = "aadhaar"
    DRIVING_LICENCE = "driving_licence"
    PASSPORT = "passport"
    INVOICE = "invoice"


class ExtractionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    status = Column(Enum(ExtractionStatus), default=ExtractionStatus.PENDING)
    raw_ocr_text = Column(Text, nullable=True)
    extracted_fields = Column(JSON, nullable=True)   # configurable output fields
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Document id={self.id} type={self.document_type} status={self.status}>"
