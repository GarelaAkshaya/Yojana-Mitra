from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from backend.core.config import get_settings
from backend.schemas.scheme import DocumentRecord

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


def checksum_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_file(file_path: str | Path) -> DocumentRecord:
    source = Path(file_path)
    if not source.exists():
        raise FileNotFoundError(source)
    suffix = source.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}")

    settings = get_settings()
    checksum = checksum_file(source)
    stored_name = f"{checksum[:12]}_{source.name}"
    stored_path = settings.paths.upload_dir / stored_name
    if source.resolve() != stored_path.resolve():
        shutil.copy2(source, stored_path)

    return DocumentRecord(
        filename=source.name,
        file_path=str(stored_path),
        file_type=suffix.lstrip("."),
        checksum=checksum,
    )
