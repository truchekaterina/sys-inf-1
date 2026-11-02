"""Общие ответы HTTP и разбор тела запроса."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse


class HttpError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def send_json(handler, status: int, payload) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Service-Key")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
    handler.send_header("Connection", "close")
    handler.end_headers()
    handler.wfile.write(body)


def send_empty(handler, status: int = 204) -> None:
    handler.send_response(status)
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Service-Key")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
    handler.send_header("Content-Length", "0")
    handler.end_headers()


def read_body(handler) -> bytes:
    if hasattr(handler, "_raw_body"):
        return handler._raw_body
    length = int(handler.headers.get("Content-Length") or "0")
    if length < 0 or length > 1_000_000:
        raise HttpError(422, "тело запроса слишком большое")
    handler._raw_body = handler.rfile.read(length) if length else b""
    return handler._raw_body


def read_json(handler) -> dict:
    raw = read_body(handler)
    if not raw:
        raise HttpError(422, "нужно тело JSON")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise HttpError(422, "тело не является JSON") from None
    if not isinstance(data, dict):
        raise HttpError(422, "тело JSON должно быть объектом")
    return data


def query_params(handler) -> dict[str, str]:
    parsed = parse_qs(urlparse(handler.path).query, keep_blank_values=False)
    result = {}
    for key, values in parsed.items():
        if values:
            result[key] = values[0]
    return result


def request_path(handler) -> str:
    return urlparse(handler.path).path


def as_text(data: dict, field: str, limit: int) -> str:
    value = data.get(field)
    if not isinstance(value, str):
        return ""
    text = value.strip()
    if len(text) > limit:
        raise HttpError(422, f"поле {field} длиннее {limit} символов")
    return text
