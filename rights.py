"""Кто какой путь людей может вызвать. Проверка стоит до обращения к реестру.

Задача на границе прав — Ф-9. Чужая роль получает 403, слой данных при этом не вызывается.
"""

from __future__ import annotations

import re

ALL = {"employee", "specialist", "auditor", "admin"}
READ_JOURNAL = {"specialist", "auditor"}

UI_MATRIX = [
    {
        "name": "me",
        "method": "GET",
        "pattern": r"^/api/v1/auth/me$",
        "roles": ALL,
        "deny": "нужен вход",
    },
    {
        "name": "chat_post",
        "method": "POST",
        "pattern": r"^/api/v1/chat/messages$",
        "roles": {"employee"},
        "deny": "чат доступен сотруднику",
    },
    {
        "name": "chat_list",
        "method": "GET",
        "pattern": r"^/api/v1/chat/messages$",
        "roles": {"employee"},
        "deny": "чат доступен сотруднику",
    },
    {
        "name": "chat_one",
        "method": "GET",
        "pattern": r"^/api/v1/chat/messages/(?P<turn_id>[0-9]+)$",
        "roles": {"employee"},
        "deny": "чат доступен сотруднику",
    },
    {
        "name": "summary",
        "method": "GET",
        "pattern": r"^/api/v1/journal/summary$",
        "roles": READ_JOURNAL,
        "deny": "журнал доступен специалисту и аудитору",
    },
    {
        "name": "journal",
        "method": "GET",
        "pattern": r"^/api/v1/journal$",
        "roles": READ_JOURNAL,
        "deny": "журнал доступен специалисту и аудитору",
    },
    {
        "name": "phrases",
        "method": "GET",
        "pattern": r"^/api/v1/journal/(?P<card_id>out-[0-9]+|[0-9]+)/phrases$",
        "roles": READ_JOURNAL,
        "deny": "журнал доступен специалисту и аудитору",
    },
    {
        "name": "delivery",
        "method": "GET",
        "pattern": r"^/api/v1/journal/(?P<card_id>out-[0-9]+|[0-9]+)/delivery$",
        "roles": READ_JOURNAL,
        "deny": "журнал доступен специалисту и аудитору",
    },
    {
        "name": "card",
        "method": "GET",
        "pattern": r"^/api/v1/journal/(?P<card_id>out-[0-9]+|[0-9]+)$",
        "roles": READ_JOURNAL,
        "deny": "журнал доступен специалисту и аудитору",
    },
    {
        "name": "calls",
        "method": "GET",
        "pattern": r"^/api/v1/calls$",
        "roles": READ_JOURNAL,
        "deny": "журнал вызовов доступен специалисту и аудитору",
    },
    {
        "name": "rules",
        "method": "GET",
        "pattern": r"^/api/v1/rules$",
        "roles": {"admin"},
        "deny": "правила доступны администратору",
    },
    {
        "name": "rules_phrases_get",
        "method": "GET",
        "pattern": r"^/api/v1/rules/phrases$",
        "roles": {"admin"},
        "deny": "правила доступны администратору",
    },
    {
        "name": "rules_phrases_put",
        "method": "PUT",
        "pattern": r"^/api/v1/rules/phrases$",
        "roles": {"admin"},
        "deny": "правила доступны администратору",
    },
    {
        "name": "rules_limits_get",
        "method": "GET",
        "pattern": r"^/api/v1/rules/limits$",
        "roles": {"admin"},
        "deny": "правила доступны администратору",
    },
    {
        "name": "rules_limits_put",
        "method": "PUT",
        "pattern": r"^/api/v1/rules/limits$",
        "roles": {"admin"},
        "deny": "правила доступны администратору",
    },
    {
        "name": "rules_delivery_get",
        "method": "GET",
        "pattern": r"^/api/v1/rules/delivery$",
        "roles": {"admin"},
        "deny": "правила доступны администратору",
    },
    {
        "name": "rules_delivery_put",
        "method": "PUT",
        "pattern": r"^/api/v1/rules/delivery$",
        "roles": {"admin"},
        "deny": "правила доступны администратору",
    },
    {
        "name": "rules_reload",
        "method": "POST",
        "pattern": r"^/api/v1/rules/reload$",
        "roles": {"admin"},
        "deny": "правила доступны администратору",
    },
]


def resolve(method: str, path: str):
    """Возвращает строку матрицы и группы регулярного выражения. Иначе бросает HttpError."""
    from http_common import HttpError

    path_known = False
    for row in UI_MATRIX:
        matched = re.fullmatch(row["pattern"], path)
        if not matched:
            continue
        path_known = True
        if row["method"] == method:
            return row, matched
    if path_known:
        raise HttpError(405, "метод не поддерживается")
    raise HttpError(404, "нет такого запроса")
