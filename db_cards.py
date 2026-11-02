"""Хранение карточек. Решение L3 или L4 сюда уже приходит готовым. Задачи З-1 и З-6."""

from __future__ import annotations

import re

from db_stand import STAND
from http_common import HttpError
from listing import row_matches, take_filters
from store_registry import REGISTRY

_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_PAIRS = {("danger_phrase", "L3"), ("topic_burst", "L4")}
_SAME = ("user_id", "question", "topic", "phrase", "code", "level")


def list_cards(params: dict) -> tuple[int, list]:
    filters = take_filters(params)
    if filters.get("delivered") == "false":
        return 200, []
    rows = REGISTRY.list_cards(
        user_id=filters.get("user_id"),
        topic=filters.get("topic"),
        code=filters.get("code"),
        level=filters.get("level"),
        since=filters.get("since"),
        date_from=filters.get("date_from"),
        date_to=filters.get("date_to"),
    )
    rows = [row for row in rows if row_matches(row, filters)]
    return 200, rows


def count_cards(params: dict) -> tuple[int, dict]:
    user_id = params.get("user_id") or ""
    topic = params.get("topic") or ""
    since = params.get("since") or ""
    if not user_id or not topic or not _ISO.fullmatch(since):
        raise HttpError(422, "для подсчёта нужны user_id, topic и since в формате UTC")
    return 200, {
        "user_id": user_id,
        "topic": topic,
        "since": since,
        "count": REGISTRY.count_danger(user_id, topic, since),
    }


def get_card(card_id: int) -> tuple[int, dict]:
    card = REGISTRY.get_card(card_id)
    if card is None:
        raise HttpError(404, "карточка не найдена")
    return 200, card


def get_phrases(card_id: int) -> tuple[int, dict]:
    _status, card = get_card(card_id)
    return 200, {"id": card["id"], "prior_phrases": card["prior_phrases"]}


def accept_card(body: dict) -> tuple[int, dict]:
    if not STAND.accept:
        raise HttpError(503, "реестр не принимает запись")
    card = _card_from_body(body)
    existing = REGISTRY.find_key(card["idempotency_key"])
    if existing is not None:
        if any(existing[field] != card[field] for field in _SAME):
            raise HttpError(409, "этот ключ уже принадлежит другой карточке")
        REGISTRY.add_delivery(existing["card_id"], card["attempt"], card["created_at"], 200)
        fresh = REGISTRY.get_card(existing["card_id"])
        return 200, fresh
    saved = REGISTRY.insert_card(card, card["attempt"], 201)
    return 201, saved


def _card_from_body(body: dict) -> dict:
    card = {
        "idempotency_key": _text(body, "idempotency_key", 80),
        "created_at": _text(body, "created_at", 40),
        "user_id": _text(body, "user_id", 64),
        "question": _text(body, "question", 2000),
        "topic": _text(body, "topic", 200),
        "phrase": _text(body, "phrase", 200),
        "snippet": _text(body, "snippet", 500),
        "code": _text(body, "code", 32),
        "level": _text(body, "level", 8),
    }
    if not all(card.values()):
        raise HttpError(422, "в карточке не хватает полей")
    if not _ISO.fullmatch(card["created_at"]):
        raise HttpError(422, "время карточки записывается в UTC")
    if (card["code"], card["level"]) not in _PAIRS:
        raise HttpError(422, "в реестр пишутся только danger_phrase/L3 и topic_burst/L4")
    attempt = body.get("attempt")
    if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 1:
        raise HttpError(422, "номер попытки — целое число от 1")
    card["attempt"] = attempt
    raw_priors = body.get("prior_phrases", [])
    if not isinstance(raw_priors, list) or len(raw_priors) > 20:
        raise HttpError(422, "прошлые фразы передаются списком")
    priors = []
    for item in raw_priors:
        if not isinstance(item, dict):
            raise HttpError(422, "прошлая фраза записана не полностью")
        prior = {
            "phrase": item.get("phrase") if isinstance(item.get("phrase"), str) else "",
            "snippet": item.get("snippet") if isinstance(item.get("snippet"), str) else "",
            "occurred_at": item.get("occurred_at") if isinstance(item.get("occurred_at"), str) else "",
        }
        if not prior["phrase"] or not prior["snippet"] or not _ISO.fullmatch(prior["occurred_at"]):
            raise HttpError(422, "прошлая фраза записана не полностью")
        priors.append(prior)
    card["prior_phrases"] = priors
    return card


def _text(body: dict, field: str, limit: int) -> str:
    value = body.get(field)
    if not isinstance(value, str):
        return ""
    text = value.strip()
    if len(text) > limit:
        raise HttpError(422, f"поле {field} длиннее {limit} символов")
    return text
