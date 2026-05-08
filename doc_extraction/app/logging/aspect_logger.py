import functools
import time
import traceback
from typing import Callable, Any
import logging

import structlog
from loguru import logger as loguru_logger
from app.core.config import get_settings

settings = get_settings()

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger()


def log_aspect(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        fn_name = f"{func.__module__}.{func.__qualname__}"
        start = time.perf_counter()
        log.info("function_call_start", function=fn_name)
        try:
            result = func(*args, **kwargs)
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            log.info("function_call_success", function=fn_name, elapsed_ms=elapsed)
            return result
        except Exception as exc:
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            log.error(
                "function_call_error",
                function=fn_name,
                elapsed_ms=elapsed,
                error=str(exc),
            )
            raise
    return wrapper


def get_logger(name: str = __name__):
    return structlog.get_logger(name)