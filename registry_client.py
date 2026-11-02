"""Вызов реестра со стороны фильтра. Люди на этот адрес не ходят."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from paths import SERVICE_HEADER
from settings_file import current


def call(method: str, path: str, query: dict | None = None, body: dict | None = None, timeout: float = 3):
    settings = current()
    url = settings.registry_url.rstrip("/") + path
    if query:
        clean = {key: value for key, value in query.items() if value is not None and value != ""}
        if clean:
            url += "?" + urlencode(clean)
    data = None
    headers = {SERVICE_HEADER: settings.token}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
            status = response.status
    except HTTPError as error:
        raw = error.read()
        status = error.code
    except URLError:
        return 0, None
    if not raw:
        return status, None
    try:
        return status, json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return status, None
