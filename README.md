# 📄 Intelligent Document Extraction Platform

A Python-based platform to extract structured data from documents (Aadhaar, Driving Licence, Passport, Invoice) using **OCR + LLM**, built with **FastAPI**, **SQLAlchemy**, **Tesseract/PaddleOCR**, and **Streamlit**.

---

## 🏗️ Architecture

```
doc_extraction/
├── app/
│   ├── api/            # FastAPI routes
│   ├── core/           # Config + DI container
│   ├── db/             # SQLAlchemy setup
│   ├── models/         # DB models (Document)
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # DocumentExtractionService (orchestrator)
│   ├── extractors/     # OCR (Tesseract/Paddle) + LLM extractors
│   ├── templates/      # Document templates (field definitions)
│   └── logging/        # Aspect-based logging (structlog + loguru)
├── tests/              # pytest unit tests
├── ui/                 # Streamlit UI
└── requirements.txt
```

### Design Patterns Used
| Pattern | Where |
|---|---|
| **Strategy** | OCR engine (Tesseract / PaddleOCR swappable) |
| **Template Method** | Document templates define extractable fields |
| **Factory** | `get_ocr_extractor(engine)` factory |
| **Dependency Injection** | `dependency-injector` container wires all components |
| **Aspect-Oriented** | `@log_aspect` decorator adds logging cross-cutting concern |

### SOLID Principles
- **S** - `DocumentExtractionService` only orchestrates; OCR/LLM are separate classes
- **O** - New doc types: add a template entry, no existing code changes
- **L** - `TesseractOCRExtractor` and `PaddleOCRExtractor` are interchangeable
- **I** - `BaseOCRExtractor` has only one method: `extract_text`
- **D** - Service depends on abstractions (`BaseOCRExtractor`), not concretions

---

## 🚀 Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Tesseract (system)
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr

# macOS
brew install tesseract
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env: set DATABASE_URL, OPENAI_API_KEY, OCR_ENGINE
```

### 4. Setup PostgreSQL database
```bash
createdb doc_extraction
# Tables are auto-created on first startup
```

---

## ▶️ Run

### Start FastAPI backend
```bash
uvicorn app.main:app --reload --port 8000
```

### Start Streamlit UI
```bash
streamlit run ui/app.py
```

### Run tests
```bash
pytest tests/ -v
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/documents/extract` | Upload doc + extract fields |
| `GET` | `/api/v1/documents/` | List all extractions |
| `GET` | `/api/v1/documents/{id}` | Get single result |
| `GET` | `/health` | Health check |

### Example: Extract Aadhaar
```bash
curl -X POST http://localhost:8000/api/v1/documents/extract \
  -F "file=@aadhaar.jpg" \
  -F "document_type=aadhaar" \
  -F "output_fields=name,dob,aadhaar_number"
```

---

## 🔄 Switching OCR Engine
In `.env`:
```
OCR_ENGINE=tesseract   # or paddleocr
```

## 🔄 Switching LLM
In `.env`:
```
LLM_MODEL=gpt-4o           # OpenAI
LLM_MODEL=gpt-4o-mini      # Cheaper option
```
For Azure OpenAI, update `LLMExtractor` to use `AzureOpenAI` client.

---

## 🖼️ Output Screenshots

### 🏠 Dashboard — Ready State
> Clean upload interface before any document is processed.

<img width="928" height="374" alt="output_0" src="https://github.com/user-attachments/assets/22c8b8ba-ae13-47e8-92ab-f598b2cf9042" />

---

### 🗂️ Extraction — All Fields (Aadhaar)
> All 6 fields extracted: name, DOB, gender, Aadhaar number, address, pincode.

<img width="728" height="399" alt="output_1" src="https://github.com/user-attachments/assets/ff1da6b3-d895-42ae-abed-6dc819177d0c" />

---

### 🎯 Extraction — Selected Fields Only
> Only `gender` and `aadhaar_number` requested — platform returns exactly those fields.

<img width="686" height="384" alt="output_2" src="https://github.com/user-attachments/assets/68d997c1-947d-4dbd-897e-8d7e48628b27" />

---

### ⚡ FastAPI Swagger Docs
> Auto-generated interactive API docs at `http://localhost:8000/docs`.

<img width="908" height="416" alt="output_3" src="https://github.com/user-attachments/assets/173c57dc-cf7d-48ab-8731-6ca74d975d0d" />

<img width="686" height="384" alt="output_2" src="https://github.com/user-attachments/assets/68d997c1-947d-4dbd-897e-8d7e48628b27" />


<img width="908" height="416" alt="output_3" src="https://github.com/user-attachments/assets/173c57dc-cf7d-48ab-8731-6ca74d975d0d" />


<img width="928" height="374" alt="output_0" src="https://github.com/user-attachments/assets/22c8b8ba-ae13-47e8-92ab-f598b2cf9042" />

