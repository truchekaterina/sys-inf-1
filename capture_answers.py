"""Снимает ответ каждого запроса живого стенда в папку скрины/api.

Стенд должен быть уже запущен: python serve.py в папке prototype.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "скрины" / "api"
UI = "http://127.0.0.1:8091"
DB = "http://127.0.0.2:8092"

NAVY = (20, 61, 82)
INK = (28, 32, 36)
MUTED = (84, 96, 104)
WHITE = (255, 255, 255)
PALE = (232, 244, 248)
DARK = (32, 36, 40)
GREEN = (166, 214, 168)


def font(size, bold=False, mono=False):
    if mono:
        name = "consola.ttf"
    else:
        name = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)


TITLE = font(26, True)
CAPTION = font(20)
SMALL = font(16)
MONO = font(18, mono=True)


def call(method: str, url: str, body=None, headers=None):
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        request.add_header(key, value)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            raw = response.read().decode("utf-8")
            status = response.status
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8")
        status = error.code
    parsed = json.loads(raw) if raw else None
    return status, parsed


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def service() -> dict:
    return {"X-Service-Key": "lab-service"}


def pretty(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def wrap(text: str, limit: int = 78) -> list[str]:
    lines = []
    for raw in text.splitlines():
        while len(raw) > limit:
            cut = raw.rfind(" ", 0, limit)
            if cut < 20:
                cut = limit
            lines.append(raw[:cut])
            raw = raw[cut:].lstrip()
        lines.append(raw)
    return lines or [""]


def draw_shot(name: str, method: str, url: str, caption: str, request_body, status: int, response):
    request_lines = []
    if request_body is not None:
        request_lines = wrap(pretty(request_body))
    response_lines = wrap(pretty(response))
    width = 1100
    head = 150
    request_h = (36 + len(request_lines) * 24 + 28) if request_lines else 0
    response_h = 36 + len(response_lines) * 24 + 36
    height = head + request_h + response_h + 40
    image = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((24, 20, width - 24, height - 20), 16, fill=PALE, outline=NAVY, width=2)
    draw.text((48, 40), f"{method}   {url}", font=TITLE, fill=NAVY)
    draw.text((48, 84), caption, font=CAPTION, fill=INK)
    draw.rounded_rectangle((48, 124, 160, 160), 8, fill=NAVY)
    draw.text((64, 128), str(status), font=TITLE, fill=WHITE)
    y = 180
    if request_lines:
        draw.text((48, y), "Что отправили", font=SMALL, fill=MUTED)
        y += 28
        box_h = len(request_lines) * 24 + 24
        draw.rounded_rectangle((48, y, width - 48, y + box_h), 10, fill=DARK)
        yy = y + 12
        for line in request_lines:
            draw.text((64, yy), line, font=MONO, fill=GREEN)
            yy += 24
        y += box_h + 20
    draw.text((48, y), "Что ответил стенд", font=SMALL, fill=MUTED)
    y += 28
    box_h = len(response_lines) * 24 + 24
    draw.rounded_rectangle((48, y, width - 48, y + box_h), 10, fill=DARK)
    yy = y + 12
    for line in response_lines:
        draw.text((64, yy), line, font=MONO, fill=GREEN)
        yy += 24
    OUT.mkdir(parents=True, exist_ok=True)
    image.save(OUT / name, "PNG")
    print(name, status)


def main():
    login_body = {"login": "employee", "password": "lab"}
    status, logged = call("POST", f"{UI}/api/v1/auth/login", login_body)
    draw_shot(
        "01_vhod.png",
        "POST",
        f"{UI}/api/v1/auth/login",
        "Сотрудник входит. В ответе токен и его номер user_17.",
        login_body,
        status,
        logged,
    )
    employee = auth(logged["token"])

    status, me = call("GET", f"{UI}/api/v1/auth/me", headers=employee)
    draw_shot(
        "02_kto.png",
        "GET",
        f"{UI}/api/v1/auth/me",
        "По токену стенд говорит, кто вошёл: сотрудник user_17.",
        None,
        status,
        me,
    )

    chat_body = {
        "question": "Как войти в узел?",
        "topic": "доступ",
        "document_text": "В файле узла пароль хранится открыто.",
    }
    status, turn = call("POST", f"{UI}/api/v1/chat/messages", chat_body, employee)
    draw_shot(
        "03_vopros.png",
        "POST",
        f"{UI}/api/v1/chat/messages",
        "В тексте есть «пароль». Сотрудник видит только «ответ отклонён».",
        chat_body,
        status,
        turn,
    )
    call(
        "POST",
        f"{UI}/api/v1/chat/messages",
        {
            "question": "Где ключ?",
            "topic": "доступ",
            "document_text": "Ключ доступа лежит в том же файле.",
        },
        employee,
    )
    call(
        "POST",
        f"{UI}/api/v1/chat/messages",
        {
            "question": "Какой узел закрыт?",
            "topic": "доступ",
            "document_text": "Это закрытый узел, туда не ходят.",
        },
        employee,
    )

    status, turns = call("GET", f"{UI}/api/v1/chat/messages", headers=employee)
    draw_shot(
        "04_svoi.png",
        "GET",
        f"{UI}/api/v1/chat/messages",
        "Свои реплики сотрудника. В каждой только то, что ему можно показать.",
        None,
        status,
        turns,
    )

    status, one = call("GET", f"{UI}/api/v1/chat/messages/1", headers=employee)
    draw_shot(
        "05_odna.png",
        "GET",
        f"{UI}/api/v1/chat/messages/1",
        "Одна реплика по номеру. Снова без фразы и без уровня.",
        None,
        status,
        one,
    )

    specialist_login, specialist_body = call(
        "POST",
        f"{UI}/api/v1/auth/login",
        {"login": "specialist", "password": "lab"},
    )
    if specialist_login != 200:
        raise SystemExit(specialist_body)
    specialist = auth(specialist_body["token"])

    status, journal = call("GET", f"{UI}/api/v1/journal", headers=specialist)
    draw_shot(
        "06_zhurnal.png",
        "GET",
        f"{UI}/api/v1/journal",
        "Специалист видит отказы: два L3 и один L4. Сотрудник этот список не открывает.",
        None,
        status,
        journal,
    )
    l4 = next(row["id"] for row in journal if row["level"] == "L4")

    status, summary = call("GET", f"{UI}/api/v1/journal/summary", headers=specialist)
    draw_shot(
        "07_svodka.png",
        "GET",
        f"{UI}/api/v1/journal/summary",
        "Сколько отказов по коду и уровню: два L3 и один L4.",
        None,
        status,
        summary,
    )

    status, card = call("GET", f"{UI}/api/v1/journal/{l4}", headers=specialist)
    draw_shot(
        "08_kartochka.png",
        "GET",
        f"{UI}/api/v1/journal/{l4}",
        "Полная карточка L4: вопрос, фраза, кусок текста и прошлые фразы.",
        None,
        status,
        card,
    )

    status, phrases = call("GET", f"{UI}/api/v1/journal/{l4}/phrases", headers=specialist)
    draw_shot(
        "09_proshlye.png",
        "GET",
        f"{UI}/api/v1/journal/{l4}/phrases",
        "Только прошлые фразы этой карточки L4.",
        None,
        status,
        phrases,
    )

    status, delivery = call("GET", f"{UI}/api/v1/journal/{l4}/delivery", headers=specialist)
    draw_shot(
        "10_dostavka.png",
        "GET",
        f"{UI}/api/v1/journal/{l4}/delivery",
        "Карточка дошла до реестра: delivered true.",
        None,
        status,
        delivery,
    )

    status, calls = call("GET", f"{UI}/api/v1/calls", headers=specialist)
    draw_shot(
        "11_vyzovy.png",
        "GET",
        f"{UI}/api/v1/calls",
        "Журнал вызовов: адрес реестра, код ответа и номер попытки. Текста документа нет.",
        None,
        status,
        calls,
    )

    admin_status, admin_body = call(
        "POST",
        f"{UI}/api/v1/auth/login",
        {"login": "admin", "password": "lab"},
    )
    if admin_status != 200:
        raise SystemExit(admin_body)
    admin = auth(admin_body["token"])

    status, rules = call("GET", f"{UI}/api/v1/rules", headers=admin)
    draw_shot(
        "12_pravila.png",
        "GET",
        f"{UI}/api/v1/rules",
        "Сводка правил. Ключ реестра не показан, стоит только token_set.",
        None,
        status,
        rules,
    )

    status, phrase_list = call("GET", f"{UI}/api/v1/rules/phrases", headers=admin)
    draw_shot(
        "13_spisok.png",
        "GET",
        f"{UI}/api/v1/rules/phrases",
        "Три фразы, которые фильтр ищет в документе.",
        None,
        status,
        phrase_list,
    )

    put_phrases = {"phrases": ["пароль", "ключ доступа", "закрытый узел"]}
    status, saved_phrases = call("PUT", f"{UI}/api/v1/rules/phrases", put_phrases, admin)
    draw_shot(
        "14_zapis_fraz.png",
        "PUT",
        f"{UI}/api/v1/rules/phrases",
        "Администратор записывает тот же список. В ответе фразы, которые теперь действуют.",
        put_phrases,
        status,
        saved_phrases,
    )

    status, limits = call("GET", f"{UI}/api/v1/rules/limits", headers=admin)
    draw_shot(
        "15_porogi.png",
        "GET",
        f"{UI}/api/v1/rules/limits",
        "Пороги: три отказа за 60 секунд превращают следующий в L4.",
        None,
        status,
        limits,
    )

    put_limits = {"N": 3, "T": 60}
    status, saved_limits = call("PUT", f"{UI}/api/v1/rules/limits", put_limits, admin)
    draw_shot(
        "16_zapis_porogov.png",
        "PUT",
        f"{UI}/api/v1/rules/limits",
        "Администратор записывает N и T. Стенд подтверждает новые пороги.",
        put_limits,
        status,
        saved_limits,
    )

    status, delivery_rules = call("GET", f"{UI}/api/v1/rules/delivery", headers=admin)
    draw_shot(
        "17_dostavka_pravila.png",
        "GET",
        f"{UI}/api/v1/rules/delivery",
        "Паузы T1 и T2, адрес реестра. Самого ключа в ответе нет.",
        None,
        status,
        delivery_rules,
    )

    put_delivery = {"T1": 0, "T2": 0, "registry_url": "http://127.0.0.2:8092"}
    status, saved_delivery = call("PUT", f"{UI}/api/v1/rules/delivery", put_delivery, admin)
    draw_shot(
        "18_zapis_dostavki.png",
        "PUT",
        f"{UI}/api/v1/rules/delivery",
        "Администратор записывает паузы и адрес. Ключ по-прежнему скрыт.",
        put_delivery,
        status,
        saved_delivery,
    )

    status, reloaded = call("POST", f"{UI}/api/v1/rules/reload", {}, admin)
    draw_shot(
        "19_peread.png",
        "POST",
        f"{UI}/api/v1/rules/reload",
        "Фильтр заново читает settings.txt. В ответе reloaded: true.",
        {},
        status,
        reloaded,
    )

    status, cards = call("GET", f"{DB}/db/v1/cards", headers=service())
    draw_shot(
        "20_kartochki.png",
        "GET",
        f"{DB}/db/v1/cards",
        "Реестр отдаёт принятые карточки. Здесь уже есть фраза и кусок текста.",
        None,
        status,
        cards,
    )

    new_card = {
        "idempotency_key": "shot-card-1",
        "created_at": "2026-10-30T08:00:00Z",
        "user_id": "user_17",
        "question": "Проверка приёма",
        "topic": "проверка",
        "phrase": "пароль",
        "snippet": "в тексте есть пароль",
        "code": "danger_phrase",
        "level": "L3",
        "attempt": 1,
        "prior_phrases": [],
    }
    status, accepted = call("POST", f"{DB}/db/v1/cards", new_card, service())
    draw_shot(
        "21_priem.png",
        "POST",
        f"{DB}/db/v1/cards",
        "Фильтр так передаёт карточку. Реестр принял её и вернул номер.",
        new_card,
        status,
        accepted,
    )

    count_url = f"{DB}/db/v1/cards/count?" + urllib.parse.urlencode(
        {"user_id": "user_17", "topic": "доступ", "since": "2020-01-01T00:00:00Z"}
    )
    status, count = call("GET", count_url, headers=service())
    draw_shot(
        "22_schet.png",
        "GET",
        f"{DB}/db/v1/cards/count",
        "Сколько карточек L3 у user_17 по теме «доступ» с 2020 года. L4 в это число не входит.",
        None,
        status,
        count,
    )

    status, full = call("GET", f"{DB}/db/v1/cards/{l4}", headers=service())
    draw_shot(
        "23_odna_kartochka.png",
        "GET",
        f"{DB}/db/v1/cards/{l4}",
        "Одна карточка реестра вместе с прошлыми фразами.",
        None,
        status,
        full,
    )

    status, prior = call("GET", f"{DB}/db/v1/cards/{l4}/phrases", headers=service())
    draw_shot(
        "24_frazi_reestra.png",
        "GET",
        f"{DB}/db/v1/cards/{l4}/phrases",
        "Только прошлые фразы этой карточки, без остальных полей.",
        None,
        status,
        prior,
    )

    status, deliveries = call("GET", f"{DB}/db/v1/deliveries", headers=service())
    draw_shot(
        "25_dostavki.png",
        "GET",
        f"{DB}/db/v1/deliveries",
        "Все доставки: какая попытка дошла и с каким кодом ответа.",
        None,
        status,
        deliveries,
    )

    status, one_delivery = call("GET", f"{DB}/db/v1/deliveries/{l4}", headers=service())
    draw_shot(
        "26_dostavka_odnoy.png",
        "GET",
        f"{DB}/db/v1/deliveries/{l4}",
        "Доставки одной карточки L4.",
        None,
        status,
        one_delivery,
    )

    status, codes = call("GET", f"{DB}/db/v1/codes", headers=service())
    draw_shot(
        "27_kody.png",
        "GET",
        f"{DB}/db/v1/codes",
        "Подписи трёх кодов. Это справочник, не журнал отказов.",
        None,
        status,
        codes,
    )

    status, levels = call("GET", f"{DB}/db/v1/levels", headers=service())
    draw_shot(
        "28_urovni.png",
        "GET",
        f"{DB}/db/v1/levels",
        "Подписи уровней L1, L3 и L4.",
        None,
        status,
        levels,
    )

    status, health = call("GET", f"{DB}/db/v1/stand/health", headers=service())
    draw_shot(
        "29_health.png",
        "GET",
        f"{DB}/db/v1/stand/health",
        "Реестр отвечает. status ok значит, что второй адрес жив.",
        None,
        status,
        health,
    )

    status, mode = call("GET", f"{DB}/db/v1/stand/mode", headers=service())
    draw_shot(
        "30_rezhim.png",
        "GET",
        f"{DB}/db/v1/stand/mode",
        "Приём включён: accept true. Карточки сейчас записываются.",
        None,
        status,
        mode,
    )

    off = {"accept": False}
    status, silent = call("PUT", f"{DB}/db/v1/stand/mode", off, service())
    draw_shot(
        "31_vykl.png",
        "PUT",
        f"{DB}/db/v1/stand/mode",
        "Приём выключен. Следующая карточка в реестр не ляжет, в чате отказ всё равно будет.",
        off,
        status,
        silent,
    )
    call("PUT", f"{DB}/db/v1/stand/mode", {"accept": True}, service())


if __name__ == "__main__":
    main()
