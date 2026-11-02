"""Журнал вызовов webhook. Функция Ф-10.

В строке есть время, адрес и код ответа. Токена и текста документа нет.
"""

from __future__ import annotations

from store_filter import FILTER


def list_calls() -> tuple[int, list]:
    return 200, FILTER.list_calls()
