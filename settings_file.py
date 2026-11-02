"""Файл config/settings.txt. Это единственное место, где живут фразы, N, T и токен.

Фильтр держит прочитанное значение в памяти. Запись с экрана «Правила»
обновляет файл и память. Реестр этот файл не читает, кроме сверки ключа:
слой данных при каждом запросе берёт из файла только service_token.
"""

from __future__ import annotations

from dataclasses import dataclass

from http_common import HttpError, now_iso
from paths import CONFIG_FILE, EXAMPLE_FILE, REGISTRY_ORIGIN


@dataclass
class Settings:
    phrases: list[str]
    n: int
    t: int
    t1: int
    t2: int
    registry_url: str
    token: str
    loaded_at: str


_CURRENT: Settings | None = None


def install_example() -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(EXAMPLE_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    reload()


def reload() -> Settings:
    global _CURRENT
    _CURRENT = _read_file(CONFIG_FILE.read_text(encoding="utf-8"))
    return _CURRENT


def current() -> Settings:
    if _CURRENT is None:
        return reload()
    return _CURRENT


def token_from_file() -> str:
    return _read_file(CONFIG_FILE.read_text(encoding="utf-8")).token


def save(settings: Settings) -> Settings:
    global _CURRENT
    settings.phrases = _unique(settings.phrases)
    _check(settings)
    lines = [f"phrase={phrase}" for phrase in settings.phrases]
    lines.extend(
        [
            f"N={settings.n}",
            f"T={settings.t}",
            f"T1={settings.t1}",
            f"T2={settings.t2}",
            f"registry_url={settings.registry_url}",
            f"service_token={settings.token}",
        ]
    )
    CONFIG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    settings.loaded_at = now_iso()
    _CURRENT = settings
    return settings


def public_view(settings: Settings) -> dict:
    return {
        "phrase_count": len(settings.phrases),
        "phrases": list(settings.phrases),
        "N": settings.n,
        "T": settings.t,
        "T1": settings.t1,
        "T2": settings.t2,
        "registry_url": settings.registry_url,
        "token_set": bool(settings.token),
        "loaded_at": settings.loaded_at,
    }


def _read_file(text: str) -> Settings:
    phrases: list[str] = []
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key == "phrase":
            if value:
                phrases.append(value)
            continue
        values[key] = value
    settings = Settings(
        phrases=_unique(phrases),
        n=_as_int(values.get("N"), "N"),
        t=_as_int(values.get("T"), "T"),
        t1=_as_int(values.get("T1"), "T1"),
        t2=_as_int(values.get("T2"), "T2"),
        registry_url=values.get("registry_url", ""),
        token=values.get("service_token", ""),
        loaded_at=now_iso(),
    )
    _check(settings)
    return settings


def _check(settings: Settings) -> None:
    if not settings.phrases:
        raise HttpError(422, "нужна хотя бы одна фраза")
    if settings.n < 1:
        raise HttpError(422, "N — целое число от 1")
    if min(settings.t, settings.t1, settings.t2) < 0:
        raise HttpError(422, "T, T1 и T2 — секунды от 0")
    if settings.registry_url != REGISTRY_ORIGIN:
        raise HttpError(422, f"адрес реестра на стенде только {REGISTRY_ORIGIN}")
    if not settings.token:
        raise HttpError(422, "токен реестра не может быть пустым")


def _as_int(value: str | None, name: str) -> int:
    if value is None or not value.lstrip("-").isdigit():
        raise HttpError(422, f"{name} должно быть целым числом")
    return int(value)


def _unique(phrases: list[str]) -> list[str]:
    seen = set()
    result = []
    for phrase in phrases:
        key = phrase.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(phrase)
    return result
