"""Чат сотрудника. Задачи З-1, З-2 и З-5.

Ответ наружу — текст модели или одна строка «ответ отклонён».
Фраза, уровень и кусок документа в этот ответ не входят.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timedelta, timezone

from catalog import MODEL_ANSWER, REFUSAL_TEXT
from http_common import HttpError, as_text, now_iso
from phrases import find_phrase, make_snippet
from registry_client import call
from settings_file import current
from store_filter import FILTER
from webhook import deliver

_LOCK = threading.Lock()


def submit(user_id: str, body: dict) -> tuple[int, dict]:
    with _LOCK:
        return _submit(user_id, body)


def list_turns(user_id: str) -> tuple[int, list]:
    return 200, [_public(row) for row in FILTER.list_turns(user_id)]


def one_turn(user_id: str, turn_id: int) -> tuple[int, dict]:
    row = FILTER.get_turn(turn_id, user_id)
    if row is None:
        raise HttpError(404, "реплика не найдена")
    return 200, _public(row)


def _submit(user_id: str, body: dict) -> tuple[int, dict]:
    question = as_text(body, "question", 2000)
    topic = as_text(body, "topic", 200)
    document = as_text(body, "document_text", 20000)
    if not question or not topic or not document:
        raise HttpError(422, "нужны вопрос, тема и текст документа")
    settings = current()
    found, at = find_phrase(document, settings.phrases)
    created = now_iso()
    if found is None:
        turn = FILTER.add_turn(created, user_id, question, topic, MODEL_ANSWER)
        return 201, _public(turn)

    since = _since(settings.t)
    already = _registry_count(user_id, topic, since) + FILTER.count_danger(user_id, topic, since)
    if already >= settings.n - 1:
        code, level = "topic_burst", "L4"
        priors = _priors(user_id, topic, since)
    else:
        code, level = "danger_phrase", "L3"
        priors = []
    card = {
        "idempotency_key": uuid.uuid4().hex,
        "created_at": created,
        "user_id": user_id,
        "question": question,
        "topic": topic,
        "phrase": found,
        "snippet": make_snippet(document, at, found),
        "code": code,
        "level": level,
        "prior_phrases": priors,
    }
    turn = FILTER.add_turn(created, user_id, question, topic, REFUSAL_TEXT)
    deliver(card)
    return 201, _public(turn)


def _since(seconds: int) -> str:
    moment = datetime.now(timezone.utc) - timedelta(seconds=seconds)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _registry_count(user_id: str, topic: str, since: str) -> int:
    status, payload = call(
        "GET",
        "/db/v1/cards/count",
        query={"user_id": user_id, "topic": topic, "since": since},
    )
    if status != 200 or not isinstance(payload, dict):
        return 0
    return int(payload.get("count") or 0)


def _priors(user_id: str, topic: str, since: str) -> list[dict]:
    status, payload = call(
        "GET",
        "/db/v1/cards",
        query={"user_id": user_id, "topic": topic, "code": "danger_phrase", "since": since},
    )
    remote = payload if status == 200 and isinstance(payload, list) else []
    local = FILTER.danger_rows(user_id, topic, since)
    items = [
        {"phrase": row["phrase"], "snippet": row["snippet"], "occurred_at": row["created_at"]}
        for row in remote
    ]
    items.extend(
        {"phrase": row["phrase"], "snippet": row["snippet"], "occurred_at": row["created_at"]}
        for row in local
    )
    items.sort(key=lambda item: item["occurred_at"])
    return items


def _public(row: dict) -> dict:
    return {
        "turn_id": row["turn_id"],
        "created_at": row["created_at"],
        "user_id": row["user_id"],
        "question": row["question"],
        "topic": row["topic"],
        "visible_text": row["visible_text"],
    }
