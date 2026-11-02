"""Общие фильтры журнала: дата, id, фраза, код, уровень, доставка."""

from __future__ import annotations

import re

from http_common import HttpError

_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_CODES = {"pass", "danger_phrase", "topic_burst"}
_LEVELS = {"L1", "L3", "L4"}


def take_filters(params: dict) -> dict:
    result = {}
    for key in ("user_id", "topic", "phrase", "since"):
        if params.get(key):
            result[key] = params[key]
    if params.get("code"):
        if params["code"] not in _CODES:
            raise HttpError(422, "неизвестный код")
        result["code"] = params["code"]
    if params.get("level"):
        if params["level"] not in _LEVELS:
            raise HttpError(422, "неизвестный уровень")
        result["level"] = params["level"]
    for key in ("date_from", "date_to"):
        if params.get(key):
            if not _DATE.fullmatch(params[key]):
                raise HttpError(422, "дата записывается как ГГГГ-ММ-ДД")
            result[key] = params[key]
    if params.get("delivered"):
        if params["delivered"] not in ("true", "false"):
            raise HttpError(422, "delivered принимает true или false")
        result["delivered"] = params["delivered"]
    return result


def row_matches(row: dict, filters: dict) -> bool:
    if filters.get("user_id") and row["user_id"] != filters["user_id"]:
        return False
    if filters.get("topic") and row["topic"] != filters["topic"]:
        return False
    if filters.get("code") and row["code"] != filters["code"]:
        return False
    if filters.get("level") and row["level"] != filters["level"]:
        return False
    if filters.get("phrase") and filters["phrase"].casefold() not in row["phrase"].casefold():
        return False
    day = row["created_at"][:10]
    if filters.get("date_from") and day < filters["date_from"]:
        return False
    if filters.get("date_to") and day > filters["date_to"]:
        return False
    if filters.get("since") and row["created_at"] < filters["since"]:
        return False
    if filters.get("delivered") == "true" and not row["delivered"]:
        return False
    if filters.get("delivered") == "false" and row["delivered"]:
        return False
    return True
