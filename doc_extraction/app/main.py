"""
FastAPI application entry point.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.db.database import init_db
from app.api.routes import router
from app.logging.aspect_logger import get_logger

log = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    log.info("app_startup", app=settings.app_name, env=settings.app_env)
    init_db()
    yield
    log.info("app_shutdown")


app = FastAPI(
    title="Intelligent Document Extraction Platform",
    description="Extract structured data from Aadhaar, Driving Licence, Passport and Invoices using OCR + LLM.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Exception handlers ────────────────────────────────────────────────────────
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    log.error("unhandled_value_error", error=str(exc), path=request.url.path)
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
