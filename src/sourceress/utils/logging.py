"""Logging utilities using loguru.

Importing this module will configure a default loguru sink that prints
colourised, structured logs to stdout.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from loguru import logger


def _default_log_path() -> Path:
    """Return default path for persistent log files."""
    return Path(os.getenv("SOURCERESS_LOG_PATH", ".cache/sourceress.log"))


# Configure root logger on import
logger.remove()
logger.add(sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"))
logger.add(_default_log_path(), rotation="1 MB", retention="10 days", level="DEBUG")

__all__ = ["logger"] 