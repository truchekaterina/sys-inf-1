"""Держит два адреса, пока окно не закроешь.

    python serve.py

Потом в браузере: http://127.0.0.1:8091
Остановка: Ctrl+C.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from paths import DB_HOST, DB_PORT, UI_HOST, UI_PORT  # noqa: E402
from runtime import start, stop  # noqa: E402


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        start()
    except OSError:
        print("Порт 8091 или 8092 уже занят.")
        print("Закрой другое окно, где запущен serve.py, и запусти снова.")
        raise SystemExit(1)
    print("ИС «Вывод → Реестр». Это окно не закрывай.", flush=True)
    print(f"Люди     http://{UI_HOST}:{UI_PORT}/docs", flush=True)
    print(f"Реестр   http://{DB_HOST}:{DB_PORT}/docs", flush=True)
    print("Остановка: Ctrl+C", flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("Останавливаю.")
        stop()


if __name__ == "__main__":
    main()
