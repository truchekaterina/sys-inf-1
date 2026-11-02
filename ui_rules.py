"""Экран «Правила». Задача З-7, функция Ф-8.

Токен записывается в файл и в ответах чтения не возвращается.
"""

from __future__ import annotations

from dataclasses import replace

from http_common import HttpError
from settings_file import current, public_view, reload, save


def rules() -> tuple[int, dict]:
    return 200, public_view(current())


def phrases() -> tuple[int, dict]:
    return 200, {"phrases": list(current().phrases)}


def put_phrases(body: dict) -> tuple[int, dict]:
    raw = body.get("phrases")
    if not isinstance(raw, list) or not raw:
        raise HttpError(422, "нужна хотя бы одна фраза")
    cleaned = []
    for item in raw:
        if not isinstance(item, str) or not item.strip():
            raise HttpError(422, "фраза должна быть непустой строкой")
        if len(item.strip()) > 200:
            raise HttpError(422, "фраза длиннее 200 символов")
        cleaned.append(item.strip())
    saved = save(replace(current(), phrases=cleaned))
    return 200, {"phrases": list(saved.phrases)}


def limits() -> tuple[int, dict]:
    settings = current()
    return 200, {"N": settings.n, "T": settings.t}


def put_limits(body: dict) -> tuple[int, dict]:
    saved = save(replace(current(), n=_whole(body, "N"), t=_whole(body, "T")))
    return 200, {"N": saved.n, "T": saved.t}


def delivery() -> tuple[int, dict]:
    settings = current()
    return 200, {
        "T1": settings.t1,
        "T2": settings.t2,
        "registry_url": settings.registry_url,
        "token_set": bool(settings.token),
    }


def put_delivery(body: dict) -> tuple[int, dict]:
    settings = current()
    token = settings.token
    if "token" in body:
        raw = body.get("token")
        if not isinstance(raw, str) or not raw.strip():
            raise HttpError(422, "токен реестра не может быть пустым")
        if len(raw.strip()) > 200:
            raise HttpError(422, "токен длиннее 200 символов")
        token = raw.strip()
    url = body.get("registry_url")
    if not isinstance(url, str) or not url.strip():
        raise HttpError(422, "нужен адрес реестра")
    saved = save(
        replace(
            settings,
            t1=_whole(body, "T1"),
            t2=_whole(body, "T2"),
            registry_url=url.strip(),
            token=token,
        )
    )
    return 200, {
        "T1": saved.t1,
        "T2": saved.t2,
        "registry_url": saved.registry_url,
        "token_set": True,
    }


def do_reload() -> tuple[int, dict]:
    view = public_view(reload())
    view["reloaded"] = True
    return 200, view


def _whole(body: dict, field: str) -> int:
    value = body.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        raise HttpError(422, f"{field} должно быть целым числом")
    return value
