"""Правило B: карточка уходит в реестр после отказа в чате.

Первая неудача — повтор. Вторая неудача — пометка «запись не дошла» в очереди фильтра.
Повтор той же карточки несёт тот же idempotency_key.
"""

from __future__ import annotations

import time

from catalog import OUTBOX_MARK
from http_common import now_iso
from registry_client import call
from settings_file import current
from store_filter import FILTER

CARD_PATH = "/db/v1/cards"


def deliver(card: dict) -> bool:
    settings = current()
    address = settings.registry_url.rstrip("/") + CARD_PATH
    for attempt in (1, 2):
        if attempt == 2 and settings.t1 > 0:
            time.sleep(settings.t1)
        status, _payload = call("POST", CARD_PATH, body={**card, "attempt": attempt})
        FILTER.add_call(now_iso(), address, status, attempt, card["idempotency_key"])
        if status in (200, 201):
            return True
    if settings.t2 > 0:
        time.sleep(settings.t2)
    FILTER.add_outbox(card, OUTBOX_MARK)
    return False
