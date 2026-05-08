from abc import ABC, abstractmethod
from PIL import Image
import io

from app.logging.aspect_logger import log_aspect, get_logger

log = get_logger(__name__)


class BaseOCRExtractor(ABC):
    """Abstract base for OCR engines."""

    @abstractmethod
    def extract_text(self, image_bytes: bytes) -> str:
        """Extract raw text from image bytes."""
        ...


class TesseractOCRExtractor(BaseOCRExtractor):
    """OCR using pytesseract (Tesseract engine)."""

    def __init__(self):
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            self._pytesseract = pytesseract
        except ImportError:
            raise RuntimeError("pytesseract is not installed. Run: pip install pytesseract")

    @log_aspect
    def extract_text(self, image_bytes: bytes) -> str:
        image = Image.open(io.BytesIO(image_bytes))
        text = self._pytesseract.image_to_string(image, lang="eng")
        log.info("tesseract_ocr_done", char_count=len(text))
        return text


class PaddleOCRExtractor(BaseOCRExtractor):
    """OCR using PaddleOCR (better for ID cards)."""

    def __init__(self):
        try:
            from paddleocr import PaddleOCR
            self._ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        except ImportError:
            raise RuntimeError("paddleocr is not installed. Run: pip install paddleocr")

    @log_aspect
    def extract_text(self, image_bytes: bytes) -> str:
        import numpy as np
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_array = np.array(image)
        result = self._ocr.ocr(img_array, cls=True)
        lines = []
        for line in result:
            for word_info in line:
                lines.append(word_info[1][0])
        text = "\n".join(lines)
        log.info("paddleocr_done", char_count=len(text))
        return text


def get_ocr_extractor(engine: str = "tesseract") -> BaseOCRExtractor:
    """Factory: return correct OCR engine based on config."""
    if engine == "paddleocr":
        return PaddleOCRExtractor()
    return TesseractOCRExtractor()