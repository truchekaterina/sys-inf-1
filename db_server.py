"""Слой реестра: /db/v1 без ролей. Адрес 127.0.0.2:8092.

Сюда ходит только фильтр и передаёт служебный ключ.
"""

from __future__ import annotations

import re

from db_cards import accept_card, count_cards, get_card, get_phrases, list_cards
from db_deliveries import deliveries_of, list_deliveries
from db_stand import STAND
from http_common import HttpError, query_params, read_json, request_path
from paths import SERVICE_HEADER
from settings_file import token_from_file
from store_registry import REGISTRY
from ui_server import _make


def make_db_handler():
    return _make("db", dispatch_db)


def dispatch_db(handler, method: str):
    if handler.headers.get(SERVICE_HEADER) != token_from_file():
        raise HttpError(401, "нужен заголовок X-Service-Key")
    path = request_path(handler)
    params = query_params(handler)
    if path == "/db/v1/cards/count" and method == "GET":
        return count_cards(params)
    if path == "/db/v1/cards" and method == "GET":
        return list_cards(params)
    if path == "/db/v1/cards" and method == "POST":
        return accept_card(read_json(handler))
    card_phrases = re.fullmatch(r"/db/v1/cards/(?P<card_id>[0-9]+)/phrases", path)
    if card_phrases and method == "GET":
        return get_phrases(int(card_phrases.group("card_id")))
    one = re.fullmatch(r"/db/v1/cards/(?P<card_id>[0-9]+)", path)
    if one and method == "GET":
        return get_card(int(one.group("card_id")))
    if path == "/db/v1/deliveries" and method == "GET":
        return list_deliveries()
    delivery = re.fullmatch(r"/db/v1/deliveries/(?P<card_id>[0-9]+)", path)
    if delivery and method == "GET":
        return deliveries_of(int(delivery.group("card_id")))
    if path == "/db/v1/codes" and method == "GET":
        return 200, REGISTRY.list_codes()
    if path == "/db/v1/levels" and method == "GET":
        return 200, REGISTRY.list_levels()
    if path == "/db/v1/stand/health" and method == "GET":
        return 200, {"status": "ok"}
    if path == "/db/v1/stand/mode" and method == "GET":
        return 200, STAND.view()
    if path == "/db/v1/stand/mode" and method == "PUT":
        body = read_json(handler)
        accept = body.get("accept")
        if not isinstance(accept, bool):
            raise HttpError(422, "accept должен быть true или false")
        STAND.accept = accept
        return 200, STAND.view()
    if path.startswith("/db/v1/"):
        raise HttpError(404, "нет такого запроса")
    raise HttpError(404, "нет такого запроса")
