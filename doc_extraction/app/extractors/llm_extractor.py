import json
from typing import Dict, Any, List, Optional

from app.core.config import get_settings
from app.templates.document_templates import DocumentTemplate
from app.logging.aspect_logger import log_aspect, get_logger

log = get_logger(__name__)
settings = get_settings()


class LLMExtractor:

    def __init__(self):
        try:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=settings.openai_api_key,
                base_url="https://api.groq.com/openai/v1",
            )
        except ImportError:
            raise RuntimeError("openai package not installed.")

    def _build_prompt(
        self,
        ocr_text: str,
        template: DocumentTemplate,
        output_fields: Optional[List[str]] = None,
    ) -> str:
        fields = output_fields if output_fields else template.fields
        fields_str = ", ".join(fields)
        return (
            f"{template.llm_prompt_hint}\n\n"
            f"Below is the raw OCR text extracted from the document:\n"
            f"---\n{ocr_text}\n---\n\n"
            f"Extract ONLY these fields: {fields_str}.\n"
            f"Return a valid JSON object with exactly these keys. "
            f"If a field is not found, set its value to null. "
            f"Do NOT include any explanation or markdown — only raw JSON."
        )

    @log_aspect
    def extract_fields(
        self,
        ocr_text: str,
        template: DocumentTemplate,
        output_fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        prompt = self._build_prompt(ocr_text, template, output_fields)
        log.info("llm_extraction_start", doc_type=template.doc_type, model=settings.llm_model)

        response = self._client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a document extraction expert. Always return valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=1000,
        )

        raw_json = response.choices[0].message.content.strip()
        raw_json = raw_json.replace("```json", "").replace("```", "").strip()

        try:
            extracted = json.loads(raw_json)
        except json.JSONDecodeError as e:
            log.error("llm_json_parse_error", error=str(e), raw=raw_json)
            raise ValueError(f"LLM returned invalid JSON: {e}")

        log.info("llm_extraction_success", fields_extracted=list(extracted.keys()))
        return extracted