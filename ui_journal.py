"""Журнал специалиста и аудитора. Задачи З-3, З-4 и чтение З-5.

Список собирает принятые карточки реестра и очередь фильтра.
В строке очереди стоит пометка «запись не дошла».
"""

from __future__ import annotations

from http_common import HttpError
from listing import row_matches, take_filters
from registry_client import call
from store_filter import FILTER


def journal(params: dict) -> tuple[int, list]:
    filters = take_filters(params)
    return 200, _rows(filters)


def summary(params: dict) -> tuple[int, dict]:
    filters = take_filters(params)
    rows = _rows(filters)
    by_code = {"danger_phrase": 0, "topic_burst": 0}
    by_level = {"L3": 0, "L4": 0}
    for row in rows:
        by_code[row["code"]] = by_code.get(row["code"], 0) + 1
        by_level[row["level"]] = by_level.get(row["level"], 0) + 1
    return 200, {"total": len(rows), "by_code": by_code, "by_level": by_level}


def card(card_key: str) -> tuple[int, dict]:
    kind, number = _split(card_key)
    if kind == "out":
        row = FILTER.get_outbox(number)
        if row is None:
            raise HttpError(404, "карточка не найдена")
        return 200, _detail(row, False, row["mark"])
    status, payload = call("GET", f"/db/v1/cards/{number}")
    if status == 404:
        raise HttpError(404, "карточка не найдена")
    if status != 200 or not isinstance(payload, dict):
        raise HttpError(503, "реестр не ответил")
    return 200, _detail(payload, True, None)


def phrases(card_key: str) -> tuple[int, dict]:
    _status, payload = card(card_key)
    return 200, {"id": payload["id"], "prior_phrases": payload["prior_phrases"]}


def delivery(card_key: str) -> tuple[int, dict]:
    kind, number = _split(card_key)
    if kind == "out":
        row = FILTER.get_outbox(number)
        if row is None:
            raise HttpError(404, "карточка не найдена")
        attempts = [
            {
                "attempt": item["attempt"],
                "sent_at": item["sent_at"],
                "http_status": item["http_status"],
                "reached": False,
            }
            for item in FILTER.calls_for(row["idempotency_key"])
        ]
        return 200, {
            "id": row["id"],
            "delivered": False,
            "mark": row["mark"],
            "attempts": attempts,
        }
    status, payload = call("GET", f"/db/v1/deliveries/{number}")
    if status == 404:
        raise HttpError(404, "карточка не найдена")
    if status != 200 or not isinstance(payload, dict):
        raise HttpError(503, "реестр не ответил")
    return 200, {
        "id": str(number),
        "delivered": True,
        "mark": None,
        "attempts": payload["attempts"],
    }


def _rows(filters: dict) -> list[dict]:
    status, payload = call(
        "GET",
        "/db/v1/cards",
        query={
            "user_id": filters.get("user_id"),
            "topic": filters.get("topic"),
            "code": filters.get("code"),
            "level": filters.get("level"),
            "phrase": filters.get("phrase"),
            "date_from": filters.get("date_from"),
            "date_to": filters.get("date_to"),
        },
    )
    remote = payload if status == 200 and isinstance(payload, list) else []
    rows = [_line(item, True) for item in remote]
    rows.extend(_line(item, False) for item in FILTER.list_outbox())
    rows = [row for row in rows if row_matches(row, filters)]
    rows.sort(key=lambda row: (row["created_at"], row["id"]))
    return rows


def _line(item: dict, delivered: bool) -> dict:
    return {
        "id": item["id"],
        "created_at": item["created_at"],
        "user_id": item["user_id"],
        "topic": item["topic"],
        "phrase": item["phrase"],
        "code": item["code"],
        "level": item["level"],
        "delivered": delivered,
    }


def _detail(item: dict, delivered: bool, mark) -> dict:
    row = _line(item, delivered)
    row["question"] = item["question"]
    row["snippet"] = item["snippet"]
    row["prior_phrases"] = item.get("prior_phrases") or []
    row["mark"] = mark
    return row


def _split(card_key: str) -> tuple[str, int]:
    if card_key.startswith("out-") and card_key[4:].isdigit():
        return "out", int(card_key[4:])
    if card_key.isdigit():
        return "registry", int(card_key)
    raise HttpError(404, "карточка не найдена")
