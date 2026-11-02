"""Запуск двух адресов в одном процессе."""

from __future__ import annotations

import threading
import time
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

from db_server import make_db_handler
from db_stand import STAND
from paths import DB_HOST, DB_PORT, UI_HOST, UI_PORT
from settings_file import install_example
from store_filter import FILTER
from store_registry import REGISTRY
from ui_server import make_ui_handler

class ReuseServer(ThreadingHTTPServer):
    allow_reuse_address = True


_SERVERS: list[ReuseServer] = []


def prepare() -> None:
    install_example()
    FILTER.reset()
    REGISTRY.reset()
    STAND.reset()


def start() -> None:
    prepare()
    ui = ReuseServer((UI_HOST, UI_PORT), make_ui_handler())
    db = ReuseServer((DB_HOST, DB_PORT), make_db_handler())
    _SERVERS[:] = [ui, db]
    for server in _SERVERS:
        threading.Thread(target=server.serve_forever, daemon=True).start()
    _wait_ready()


def stop() -> None:
    for server in _SERVERS:
        server.shutdown()
        server.server_close()
    _SERVERS.clear()


def _wait_ready() -> None:
    for url in (f"http://{UI_HOST}:{UI_PORT}/docs", f"http://{DB_HOST}:{DB_PORT}/docs"):
        last_error = None
        for _ in range(50):
            try:
                with urlopen(url, timeout=0.5) as response:
                    response.read()
                last_error = None
                break
            except OSError as error:
                last_error = error
                time.sleep(0.05)
        if last_error is not None:
            stop()
            raise RuntimeError(f"не открылся {url}") from last_error
