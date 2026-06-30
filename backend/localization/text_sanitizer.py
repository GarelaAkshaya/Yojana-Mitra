from __future__ import annotations

import re
import unicodedata

from backend.localization.translator import language_code

CORRUPTED_TEXT_RE = re.compile(r"(?:\uFFFD|ԱՂՄ|࿌|[\u0700-\u074F\u0780-\u07BF\u0530-\u058F])+", re.U)
CONTROL_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")

SCRIPT_RANGES = {
    "hi": (r"\u0900-\u097F",),
    "te": (r"\u0C00-\u0C7F",),
}


def sanitize_text(value: object) -> str:
    text = str(value or "")
    text = unicodedata.normalize("NFC", text)
    text = CONTROL_RE.sub(" ", text)
    text = CORRUPTED_TEXT_RE.sub(" ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sanitize_items(items: object) -> list[str]:
    if not isinstance(items, list):
        return []
    return [cleaned for item in items if (cleaned := sanitize_text(item))]


def mostly_selected_language(text: str, language: str) -> bool:
    code = language_code(language)
    ranges = SCRIPT_RANGES.get(code)
    if not ranges:
        return True
    target = len(re.findall(f"[{''.join(ranges)}]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    devanagari = len(re.findall(r"[\u0900-\u097F]", text))
    telugu = len(re.findall(r"[\u0C00-\u0C7F]", text))
    other_indic = (devanagari + telugu) - target
    return target >= max(latin, other_indic, 1)
