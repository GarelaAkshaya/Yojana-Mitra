from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"-\n(?=\w)", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_list_block(block: str) -> list[str]:
    lines = re.split(r"\n|;|•|\u2022", block)
    cleaned: list[str] = []
    for line in lines:
        item = re.sub(r"^\s*[-*\d.)]+", "", line).strip(" :\t")
        if len(item) >= 3:
            cleaned.append(item)
    return cleaned
