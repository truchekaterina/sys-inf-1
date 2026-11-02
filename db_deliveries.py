"""Доставки принятых карточек. Задача З-6. Недоставленные сюда не попадают."""

from __future__ import annotations

from http_common import HttpError
from store_registry import REGISTRY


def list_deliveries() -> tuple[int, list]:
    return 200, REGISTRY.list_deliveries()


def deliveries_of(card_id: int) -> tuple[int, dict]:
    if REGISTRY.get_card(card_id) is None:
        raise HttpError(404, "карточка не найдена")
    return 200, {"id": str(card_id), "attempts": REGISTRY.list_deliveries(card_id)}
