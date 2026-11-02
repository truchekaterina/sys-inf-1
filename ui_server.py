"""Слой людей: вход, роли и маршруты /api/v1. Адрес 127.0.0.1:8091."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from catalog import ACCOUNTS, TOKEN_PREFIX
from http_common import HttpError, query_params, read_body, read_json, request_path, send_empty, send_json
from rights import resolve
from ui_calls import list_calls
from ui_chat import list_turns, one_turn, submit
from ui_journal import card, delivery, journal, phrases, summary
from ui_rules import (
    delivery as rules_delivery,
    do_reload,
    limits,
    phrases as rule_phrases,
    put_delivery,
    put_limits,
    put_phrases,
    rules,
)
from web import try_serve


def make_ui_handler():
    return _make("ui", dispatch_ui)


def dispatch_ui(handler, method: str):
    path = request_path(handler)
    if method == "POST" and path == "/api/v1/auth/login":
        return login(read_json(handler))
    account = _account(handler)
    row, matched = resolve(method, path)
    if account["role"] not in row["roles"]:
        raise HttpError(403, row["deny"])
    groups = matched.groupdict()
    params = query_params(handler)
    name = row["name"]
    if name == "me":
        return 200, {"login": account["login"], "role": account["role"], "user_id": account["user_id"]}
    if name == "chat_post":
        return submit(account["user_id"], read_json(handler))
    if name == "chat_list":
        return list_turns(account["user_id"])
    if name == "chat_one":
        return one_turn(account["user_id"], int(groups["turn_id"]))
    if name == "summary":
        return summary(params)
    if name == "journal":
        return journal(params)
    if name == "phrases":
        return phrases(groups["card_id"])
    if name == "delivery":
        return delivery(groups["card_id"])
    if name == "card":
        return card(groups["card_id"])
    if name == "calls":
        return list_calls()
    if name == "rules":
        return rules()
    if name == "rules_phrases_get":
        return rule_phrases()
    if name == "rules_phrases_put":
        return put_phrases(read_json(handler))
    if name == "rules_limits_get":
        return limits()
    if name == "rules_limits_put":
        return put_limits(read_json(handler))
    if name == "rules_delivery_get":
        return rules_delivery()
    if name == "rules_delivery_put":
        return put_delivery(read_json(handler))
    if name == "rules_reload":
        return do_reload()
    raise HttpError(404, "нет такого запроса")


def login(body: dict):
    name = body.get("login")
    password = body.get("password")
    account = ACCOUNTS.get(name) if isinstance(name, str) else None
    if account is None or not isinstance(password, str) or password != account["password"]:
        raise HttpError(401, "неверный логин или пароль")
    return 200, {
        "token": TOKEN_PREFIX + name,
        "role": account["role"],
        "user_id": account["user_id"],
    }


def _account(handler) -> dict:
    header = handler.headers.get("Authorization") or ""
    if not header.startswith("Bearer "):
        raise HttpError(401, "нужен заголовок Authorization")
    token = header.removeprefix("Bearer ").strip()
    if not token.startswith(TOKEN_PREFIX):
        raise HttpError(401, "неизвестный токен")
    name = token.removeprefix(TOKEN_PREFIX)
    account = ACCOUNTS.get(name)
    if account is None:
        raise HttpError(401, "неизвестный токен")
    return {"login": name, "role": account["role"], "user_id": account["user_id"]}


def _make(kind: str, dispatch):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self):  # noqa: N802
            self._go("GET")

        def do_POST(self):  # noqa: N802
            self._go("POST")

        def do_PUT(self):  # noqa: N802
            self._go("PUT")

        def do_OPTIONS(self):  # noqa: N802
            send_empty(self, 204)

        def _go(self, method: str) -> None:
            try:
                if try_serve(self, kind):
                    return
                if method in ("POST", "PUT"):
                    read_body(self)
                status, payload = dispatch(self, method)
                send_json(self, status, payload)
            except HttpError as error:
                send_json(self, error.status, {"error": error.message})
            except Exception:
                import traceback

                traceback.print_exc()
                send_json(self, 500, {"error": "внутренняя ошибка стенда"})

        def log_message(self, fmt: str, *args) -> None:
            return

    return Handler
