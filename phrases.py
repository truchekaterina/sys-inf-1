"""Поиск фразы списка в тексте документа. Задача З-2, функция Ф-2.

В карточку попадает фраза из списка и кусок исходного текста вокруг неё.
Сам список в реестр не копируется.
"""

from __future__ import annotations


def find_phrase(text: str, phrases: list[str]) -> tuple[str | None, int]:
    folded = text.casefold()
    ordered = sorted((item for item in phrases if item), key=len, reverse=True)
    for phrase in ordered:
        at = folded.find(phrase.casefold())
        if at >= 0:
            return phrase, at
    return None, -1


def make_snippet(text: str, at: int, phrase: str, radius: int = 24) -> str:
    start = max(0, at - radius)
    end = min(len(text), at + len(phrase) + radius)
    chunk = " ".join(text[start:end].split())
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(text) else ""
    return f"{prefix}{chunk}{suffix}"
