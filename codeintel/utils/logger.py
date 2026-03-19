"""Minimal logger for CodeIntel."""

import logging
import sys


def get_logger(name: str = "codeintel") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
