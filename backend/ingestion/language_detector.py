from __future__ import annotations


def detect_language(text: str) -> str:
    devanagari = sum(1 for char in text if "\u0900" <= char <= "\u097f")
    telugu = sum(1 for char in text if "\u0c00" <= char <= "\u0c7f")
    latin = sum(1 for char in text if char.isascii() and char.isalpha())
    if telugu > max(devanagari, latin):
        return "te"
    if devanagari > max(telugu, latin):
        return "hi"
    if latin:
        return "en"
    return "unknown"
