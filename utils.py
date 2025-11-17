"""Utility functions for the documentation enricher."""
import logging
import json
from typing import Any, Dict
from rich.logging import RichHandler
from config import Config


def setup_logging():
    """Configure logging with rich handler."""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger("documenter")


def safe_json_loads(text: str) -> Dict[str, Any]:
    """Safely load JSON from text, handling errors."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON: {e}")
        return {}


def sanitize_field_name(name: str) -> str:
    """Sanitize field name for use in generated documentation."""
    return name.strip().replace(" ", "_").lower()


def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

