"""
Dependency Injection Container using dependency-injector.
All components are wired here — following Dependency Inversion Principle.
"""
from dependency_injector import containers, providers

from app.core.config import get_settings
from app.extractors.ocr_extractor import get_ocr_extractor
from app.extractors.llm_extractor import LLMExtractor
from app.services.extraction_service import DocumentExtractionService

settings = get_settings()


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # OCR Extractor (strategy pattern via factory)
    ocr_extractor = providers.Singleton(
        get_ocr_extractor,
        engine=settings.ocr_engine,
    )

    # LLM Extractor
    llm_extractor = providers.Singleton(LLMExtractor)

    # Main Service
    extraction_service = providers.Singleton(
        DocumentExtractionService,
        ocr_extractor=ocr_extractor,
        llm_extractor=llm_extractor,
    )
