from __future__ import annotations

import logging
from pathlib import Path

from backend.core.config import get_settings


def configure_logging(level: int = logging.INFO) -> None:
    settings = get_settings()
    log_dir = Path(settings.paths.data_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "yojana_mitra.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
