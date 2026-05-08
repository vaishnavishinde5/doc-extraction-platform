"""
Unit tests for the Document Extraction Platform.
Run: pytest tests/ -v
"""
import pytest
from unittest.mock import MagicMock, patch
from app.templates.document_templates import get_template, TEMPLATES
from app.models.document import DocumentType, ExtractionStatus
from app.services.extraction_service import DocumentExtractionService


# ── Template Tests ────────────────────────────────────────────────────────────
class TestDocumentTemplates:
    def test_all_templates_exist(self):
        for doc_type in ["aadhaar", "driving_licence", "passport", "invoice"]:
            template = get_template(doc_type)
            assert template is not None
            assert len(template.fields) > 0
            assert len(template.llm_prompt_hint) > 0

    def test_invalid_template_raises(self):
        with pytest.raises(ValueError, match="No template found"):
            get_template("unknown_type")

    def test_aadhaar_has_required_fields(self):
        t = get_template("aadhaar")
        assert "aadhaar_number" in t.fields
        assert "name" in t.fields
        assert "dob" in t.fields

    def test_passport_has_mrz_fields(self):
        t = get_template("passport")
        assert "mrz_line1" in t.fields
        assert "mrz_line2" in t.fields

    def test_invoice_has_financial_fields(self):
        t = get_template("invoice")
        assert "total_amount" in t.fields
        assert "invoice_number" in t.fields


# ── OCR Tests ─────────────────────────────────────────────────────────────────
class TestOCRExtractor:
    def test_tesseract_extractor_returns_string(self):
        with patch("pytesseract.image_to_string", return_value="Test OCR Output"):
            from app.extractors.ocr_extractor import TesseractOCRExtractor
            extractor = TesseractOCRExtractor.__new__(TesseractOCRExtractor)
            mock_pytesseract = MagicMock()
            mock_pytesseract.image_to_string.return_value = "Test OCR Output"
            extractor._pytesseract = mock_pytesseract

            from PIL import Image
            import io
            img = Image.new("RGB", (100, 100), color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            result = extractor.extract_text(buf.getvalue())
            assert isinstance(result, str)
            assert result == "Test OCR Output"


# ── LLM Extractor Tests ───────────────────────────────────────────────────────
class TestLLMExtractor:
    def test_build_prompt_contains_fields(self):
        from app.extractors.llm_extractor import LLMExtractor
        extractor = LLMExtractor.__new__(LLMExtractor)
        template = get_template("aadhaar")
        prompt = extractor._build_prompt("some ocr text", template, ["name", "dob"])
        assert "name" in prompt
        assert "dob" in prompt
        assert "some ocr text" in prompt

    def test_build_prompt_uses_all_fields_when_none(self):
        from app.extractors.llm_extractor import LLMExtractor
        extractor = LLMExtractor.__new__(LLMExtractor)
        template = get_template("aadhaar")
        prompt = extractor._build_prompt("ocr text", template, None)
        for field in template.fields:
            assert field in prompt


# ── Service Tests ─────────────────────────────────────────────────────────────
class TestDocumentExtractionService:
    def _make_service(self):
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "Raw OCR text from document"
        mock_llm = MagicMock()
        mock_llm.extract_fields.return_value = {"name": "John Doe", "dob": "01/01/1990"}
        return DocumentExtractionService(mock_ocr, mock_llm), mock_ocr, mock_llm

    def test_process_document_success(self):
        service, mock_ocr, mock_llm = self._make_service()
        mock_db = MagicMock()

        # Simulate db.refresh populating the object
        def mock_refresh(obj):
            obj.id = 1
            obj.status = ExtractionStatus.SUCCESS
            obj.extracted_fields = {"name": "John Doe"}

        mock_db.refresh.side_effect = mock_refresh

        result = service.process_document(
            db=mock_db,
            filename="test_aadhaar.jpg",
            image_bytes=b"fake_image_bytes",
            document_type=DocumentType.AADHAAR,
        )

        mock_ocr.extract_text.assert_called_once()
        mock_llm.extract_fields.assert_called_once()
        mock_db.add.assert_called_once()
        assert mock_db.commit.call_count >= 1

    def test_process_document_handles_ocr_failure(self):
        mock_ocr = MagicMock()
        mock_ocr.extract_text.side_effect = RuntimeError("OCR engine failed")
        mock_llm = MagicMock()
        service = DocumentExtractionService(mock_ocr, mock_llm)

        mock_db = MagicMock()
        mock_db.refresh.side_effect = lambda obj: None

        result = service.process_document(
            db=mock_db,
            filename="bad.jpg",
            image_bytes=b"bad_bytes",
            document_type=DocumentType.PASSPORT,
        )

        # Should set status to FAILED without raising
        assert mock_db.commit.call_count >= 1
        mock_llm.extract_fields.assert_not_called()
