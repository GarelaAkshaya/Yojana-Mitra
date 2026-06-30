from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
_BOOTSTRAPPED = False


def ensure_project_root() -> Path:
    root = str(PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    return PROJECT_ROOT


def bootstrap_project() -> Path:
    global _BOOTSTRAPPED
    project_root = ensure_project_root()
    if not _BOOTSTRAPPED:
        try:
            from backend.core.logging_setup import configure_logging

            configure_logging()
        except Exception:
            logging.basicConfig(level=logging.INFO)
            logging.getLogger(__name__).exception("Application logging could not be fully configured")
        _BOOTSTRAPPED = True
    return project_root
