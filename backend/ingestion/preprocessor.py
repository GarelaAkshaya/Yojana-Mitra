from __future__ import annotations

from pathlib import Path


def preprocess_image(path: str | Path) -> str:
    """Prepare an image for OCR when Pillow/OpenCV are available.

    The current implementation is intentionally conservative: it validates
    that the image can be opened and returns the original path. Heavy
    preprocessing can be added without changing downstream contracts.
    """
    try:
        from PIL import Image

        with Image.open(path) as image:
            image.verify()
    except ImportError:
        return str(path)
    return str(path)
