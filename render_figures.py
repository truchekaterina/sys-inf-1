"""Схемы для отчёта. Запуск: python scripts/render_figures.py"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "рисунки"
NAVY = (20, 61, 82)
INK = (28, 32, 36)
MUTED = (84, 96, 104)
PALE = (232, 244, 248)
GREEN = (232, 245, 236)
RED = (255, 236, 232)
SAND = (255, 248, 236)
LINE = (20, 61, 82)
WHITE = (255, 255, 255)


def font(size, bold=False):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)


FB = font(22, True)
F = font(18)
FS = font(16)
FT = font(28, True)


def canvas(w, h):
    img = Image.new("RGB", (w, h), WHITE)
    return img, ImageDraw.Draw(img)


def box(draw, x, y, w, h, fill):
    draw.rounded_rectangle((x, y, x + w, y + h), 14, fill=fill, outline=NAVY, width=2)


def label(draw, x, y, text, fnt=F, fill=INK):
    draw.text((x, y), text, font=fnt, fill=fill)


def arrow_down(draw, x, y1, y2):
    draw.line((x, y1, x, y2 - 10), fill=LINE, width=3)
    draw.polygon([(x - 7, y2 - 12), (x + 7, y2 - 12), (x, y2)], fill=LINE)


def arrow_right(draw, x1, x2, y):
    draw.line((x1, y, x2 - 10, y), fill=LINE, width=3)
    draw.polygon([(x2 - 12, y - 7), (x2 - 12, y + 7), (x2, y)], fill=LINE)


def save(img, name):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    img.save(path, "PNG")
    print(path)


def architecture():
    img, d = canvas(1280, 860)
    label(d, 48, 28, "Два адреса. Человек в реестр сам не ходит", FT, NAVY)
    label(d, 48, 72, "Сначала фильтр решает, можно ли показать ответ. Реестр только хранит карточку отказа.", FS, MUTED)

    box(d, 340, 120, 600, 110, PALE)
    label(d, 364, 138, "Браузер, страница Swagger", FB, NAVY)
    label(d, 364, 174, "Человек нажимает Execute.", F)
    label(d, 364, 202, "Это экран. Отдельного сайта нет.", F)

    arrow_down(d, 640, 230, 280)
    label(d, 656, 240, "вопрос и токен роли", FS, MUTED)

    box(d, 80, 290, 760, 210, PALE)
    label(d, 104, 308, "Фильтр    127.0.0.1:8091", FB, NAVY)
    label(d, 104, 348, "1. Проверяет, какая роль вошла.", F)
    label(d, 104, 378, "2. Ищет в тексте документа фразу из списка.", F)
    label(d, 104, 408, "3. Решает: отдать ответ модели или написать «ответ отклонён».", F)
    label(d, 104, 438, "4. Если отказов по теме уже много, ставит уровень L4.", F)
    label(d, 104, 468, "Сотрудник фразу и уровень в ответе не видит.", F)

    box(d, 880, 290, 352, 210, SAND)
    label(d, 904, 308, "config/settings.txt", FB, NAVY)
    label(d, 904, 352, "Фразы списка.", F)
    label(d, 904, 382, "Пороги N, T, T1, T2.", F)
    label(d, 904, 412, "Адрес реестра и токен.", F)
    label(d, 904, 450, "В базу реестра файл", F)
    label(d, 904, 478, "не копируется.", F)

    arrow_down(d, 460, 500, 560)
    label(d, 476, 516, "карточка, только если был отказ", FS, MUTED)

    box(d, 80, 570, 760, 180, PALE)
    label(d, 104, 588, "Реестр    127.0.0.2:8092", FB, NAVY)
    label(d, 104, 628, "Принимает карточку по ключу lab-service.", F)
    label(d, 104, 658, "Хранит, кто спросил, какую фразу нашли и кусок документа.", F)
    label(d, 104, 688, "Роль здесь не проверяется: в реестр ходит только фильтр.", F)
    label(d, 104, 718, "Повтор той же карточки вторую строку не создаёт.", F)

    box(d, 880, 570, 352, 180, GREEN)
    label(d, 904, 588, "data/registry.db", FB, NAVY)
    label(d, 904, 628, "Только принятые карточки.", F)
    label(d, 904, 662, "Код pass сюда не пишется.", F)
    label(d, 904, 696, "Чат без фразы — в filter.db.", F)

    save(img, "01_dva_adresa.png")


def question_flow():
    img, d = canvas(1280, 980)
    label(d, 48, 28, "Один вопрос: от текста документа до журнала", FT, NAVY)

    box(d, 340, 90, 600, 90, PALE)
    label(d, 364, 108, "1. Сотрудник user_17", FB, NAVY)
    label(d, 364, 144, "Пишет вопрос, тему и текст документа.", F)
    arrow_down(d, 640, 180, 230)

    box(d, 340, 240, 600, 90, PALE)
    label(d, 364, 258, "2. Фильтр ищет фразу", FB, NAVY)
    label(d, 364, 294, "«пароль», «ключ доступа», «закрытый узел».", F)
    arrow_down(d, 640, 330, 390)

    box(d, 390, 400, 500, 70, SAND)
    label(d, 414, 422, "Фраза в тексте есть?", FB, NAVY)

    arrow_down(d, 280, 470, 540)
    label(d, 120, 490, "нет", FS, MUTED)
    box(d, 70, 550, 420, 150, GREEN)
    label(d, 94, 568, "L1, код pass", FB, NAVY)
    label(d, 94, 608, "В чате текст ответа модели.", F)
    label(d, 94, 638, "Карточка не создаётся.", F)
    label(d, 94, 668, "Реестр не вызывается.", F)

    arrow_down(d, 1000, 470, 540)
    label(d, 1016, 490, "да", FS, MUTED)
    box(d, 790, 550, 440, 150, RED)
    label(d, 814, 568, "Отказ уже в чате", FB, NAVY)
    label(d, 814, 608, "Одна строка: «ответ отклонён».", F)
    label(d, 814, 638, "Первые отказы по теме — L3.", F)
    label(d, 814, 668, "Третий за время T — L4.", F)

    arrow_down(d, 1000, 700, 760)
    box(d, 760, 770, 470, 160, PALE)
    label(d, 784, 788, "3. Карточка уходит в реестр", FB, NAVY)
    label(d, 784, 828, "Кто, вопрос, фраза, кусок текста.", F)
    label(d, 784, 858, "Если реестр молчит — повтор.", F)
    label(d, 784, 888, "Если молчит снова — «запись не дошла».", F)

    save(img, "02_odin_vopros.png")


def roles():
    img, d = canvas(1280, 560)
    label(d, 48, 28, "Четыре роли. Чужой кнопки нет", FT, NAVY)
    label(d, 48, 72, "Пароль у всех один: lab. Проверка роли происходит до обращения к реестру.", FS, MUTED)
    items = [
        (48, PALE, "Сотрудник", "lab.employee", "Пишет вопрос.", "Видит ответ или", "«ответ отклонён».", "Журнал закрыт."),
        (364, SAND, "Специалист", "lab.specialist", "Сам открывает журнал.", "Читает, кто спросил", "и из-за какой фразы.", "Ничего не правит."),
        (680, SAND, "Аудитор", "lab.auditor", "Тот же журнал.", "Только чтение.", "Правила записать", "не может."),
        (996, GREEN, "Администратор", "lab.admin", "Меняет список фраз,", "N, T и адрес.", "Журнал отказов", "не открывает."),
    ]
    for x, fill, title, token, *lines in items:
        box(d, x, 130, 236, 360, fill)
        label(d, x + 20, 150, title, FB, NAVY)
        label(d, x + 20, 190, token, FS, MUTED)
        y = 240
        for line in lines:
            label(d, x + 20, y, line, F)
            y += 36
    save(img, "03_roli.png")


def levels():
    img, d = canvas(1280, 460)
    label(d, 48, 28, "Три уровня. Уровня L2 нет", FT, NAVY)
    cols = [
        (48, GREEN, "L1", "pass", "Фразы в тексте нет.", "Ответ выдан.", "В реестр не пишется."),
        (460, RED, "L3", "danger_phrase", "Фраза найдена.", "Выдачи нет.", "Полная карточка."),
        (872, SAND, "L4", "topic_burst", "Третий отказ за время T.", "Первые два остаются L3.", "В карточке прошлые фразы."),
    ]
    for x, fill, level, code, *lines in cols:
        box(d, x, 110, 360, 290, fill)
        label(d, x + 24, 132, level, FT, NAVY)
        label(d, x + 24, 180, code, FB, NAVY)
        y = 230
        for line in lines:
            label(d, x + 24, y, line, F)
            y += 36
    save(img, "04_urovni.png")


def data_map():
    img, d = canvas(1280, 780)
    label(d, 48, 28, "Где какое сведение живёт", FT, NAVY)
    label(d, 48, 72, "Одно и то же не хранится в двух местах. Фраза списка — только в файле.", FS, MUTED)

    box(d, 48, 130, 380, 580, SAND)
    label(d, 72, 150, "Файл настроек", FB, NAVY)
    label(d, 72, 190, "config/settings.txt", FS, MUTED)
    for i, line in enumerate([
        "пароль",
        "ключ доступа",
        "закрытый узел",
        "N = 3, окно T",
        "паузы T1 и T2",
        "адрес реестра",
        "токен lab-service",
    ]):
        label(d, 72, 240 + i * 40, line, F)
    label(d, 72, 640, "Меняет администратор.", FS, MUTED)

    box(d, 460, 130, 380, 580, GREEN)
    label(d, 484, 150, "База фильтра", FB, NAVY)
    label(d, 484, 190, "data/filter.db", FS, MUTED)
    for i, line in enumerate([
        "Реплика чата:",
        "вопрос и «ответ отклонён».",
        "Фразы в ней нет.",
        "",
        "Очередь, если реестр",
        "не принял карточку.",
        "Пометка «запись не дошла».",
        "",
        "Журнал вызовов:",
        "адрес и код ответа.",
    ]):
        label(d, 484, 240 + i * 34, line, F)

    box(d, 872, 130, 360, 580, PALE)
    label(d, 896, 150, "База реестра", FB, NAVY)
    label(d, 896, 190, "data/registry.db", FS, MUTED)
    for i, line in enumerate([
        "Карточка отказа:",
        "кто, вопрос, тема,",
        "фраза, кусок документа,",
        "код и уровень.",
        "",
        "Прошлые фразы для L4.",
        "",
        "Доставки:",
        "какая попытка дошла.",
        "Код pass сюда не попадает.",
    ]):
        label(d, 896, 240 + i * 34, line, F)
    save(img, "05_dannye.png")


def clean_card(draw, x, y, w, name, title, lines, fill):
    height = 108 + len(lines) * 34 + 20
    box(draw, x, y, w, height, fill)
    name_font = FB if len(name) > 12 else FT
    label(draw, x + 24, y + 18, name, name_font, NAVY)
    label(draw, x + 24, y + 58, title, FB, NAVY)
    yy = y + 104
    for line in lines:
        label(draw, x + 24, yy, line, F)
        yy += 34
    return height


def dashed(draw, x, y1, y2):
    y = y1
    while y < y2 - 12:
        draw.line((x, y, x, min(y + 8, y2 - 12)), fill=LINE, width=3)
        y += 16


def tables():
    img, d = canvas(1560, 1540)
    label(d, 48, 28, "Две базы. В каждой свои таблицы", FT, NAVY)
    label(d, 48, 72, "Стрелка показывает связь. Список фраз в таблицах нет: он лежит в settings.txt.", FS, MUTED)

    label(d, 48, 124, "База фильтра    data/filter.db", FB, NAVY)
    label(d, 820, 124, "База реестра    data/registry.db", FB, NAVY)

    turns_h = clean_card(d, 48, 168, 720, "turns", "Реплика чата", [
        "turn_id — номер реплики, ключ строки",
        "created_at — время вопроса",
        "user_id — кто спросил",
        "question — вопрос",
        "topic — тема",
        "visible_text — что увидел сотрудник",
        "С другими таблицами не связана.",
    ], GREEN)

    out_y = 168 + turns_h + 24
    out_h = clean_card(d, 48, out_y, 720, "outbox", "Не дошло до реестра", [
        "outbox_id — номер в очереди, ключ строки",
        "created_at — время отказа",
        "user_id — кто спросил",
        "question — вопрос",
        "topic — тема",
        "phrase — найденная фраза",
        "snippet — кусок документа",
        "code — код отказа",
        "level — уровень",
        "idempotency_key — ключ отправки",
        "prior_json — прошлые фразы, если это L4",
        "mark — пометка «запись не дошла»",
    ], SAND)

    call_y = out_y + out_h + 72
    clean_card(d, 48, call_y, 720, "calls", "Попытка отправки", [
        "call_id — номер попытки, ключ строки",
        "sent_at — когда отправили",
        "address — адрес реестра",
        "http_status — код ответа, 0 если связи не было",
        "attempt — попытка 1 или 2",
        "idempotency_key — тот же ключ, что в outbox",
    ], PALE)
    dashed(d, 408, out_y + out_h, call_y)
    d.polygon([(401, call_y - 12), (415, call_y - 12), (408, call_y)], fill=LINE)
    label(d, 428, out_y + out_h + 22, "один ключ отправки", FS, MUTED)

    cards_h = clean_card(d, 820, 168, 692, "cards", "Принятая карточка отказа", [
        "card_id — номер карточки, ключ строки",
        "created_at — время отказа",
        "user_id — кто спросил",
        "question — вопрос",
        "topic — тема",
        "phrase — найденная фраза",
        "snippet — кусок документа",
        "code — danger_phrase или topic_burst",
        "level — L3 или L4",
        "idempotency_key — повтор не создаёт вторую строку",
        "Только L3 и L4. Код pass сюда не пишется.",
    ], PALE)

    child_y = 168 + cards_h + 64
    prior_h = clean_card(d, 820, child_y, 330, "card_prior_phrases", "Прошлые фразы L4", [
        "id — номер строки, ключ",
        "card_id — ссылка на cards",
        "phrase — прошлая фраза",
        "snippet — прошлый кусок",
        "occurred_at — когда уже было",
    ], SAND)
    del_h = clean_card(d, 1182, child_y, 330, "deliveries", "Какая попытка дошла", [
        "delivery_id — номер, ключ",
        "card_id — ссылка на cards",
        "attempt — попытка 1 или 2",
        "sent_at — когда приняли",
        "http_status — код ответа",
        "reached — 1, если строка легла",
    ], SAND)
    cards_bottom = 168 + cards_h
    arrow_down(d, 985, cards_bottom, child_y)
    arrow_down(d, 1347, cards_bottom, child_y)
    label(d, 1010, cards_bottom + 16, "card_id", FS, MUTED)

    dict_y = child_y + max(prior_h, del_h) + 28
    clean_card(d, 820, dict_y, 330, "codes", "Подписи кодов", [
        "code — слово кода, ключ",
        "title — что это слово значит",
        "Стрелки к cards нет.",
    ], GREEN)
    clean_card(d, 1182, dict_y, 330, "levels", "Подписи уровней", [
        "level — L1, L3 или L4, ключ",
        "meaning — когда ставится",
        "Стрелки к cards нет.",
    ], GREEN)

    save(img, "07_tablitsy.png")


def delivery():
    img, d = canvas(1280, 420)
    label(d, 48, 28, "Отказ в чате уже сделан. Запись карточки идёт следом", FT, NAVY)
    steps = [
        (48, "1", "Чат", "Сотрудник уже видит\n«ответ отклонён»."),
        (360, "2", "Первая отправка", "Фильтр шлёт карточку\nна 127.0.0.2:8092."),
        (672, "3", "Повтор", "Если реестр не принял,\nта же карточка уходит ещё раз."),
        (984, "4", "Пометка", "Если снова не принял,\nв журнале «запись не дошла»."),
    ]
    for i, (x, num, title, text) in enumerate(steps):
        box(d, x, 140, 250, 200, PALE if i < 3 else RED)
        label(d, x + 20, 160, num, FT, NAVY)
        label(d, x + 70, 168, title, FB, NAVY)
        y = 230
        for line in text.split("\n"):
            label(d, x + 20, y, line, F)
            y += 34
        if i < 3:
            arrow_right(d, x + 250, x + 312, 240)
    save(img, "06_dostavka.png")


def main():
    architecture()
    question_flow()
    roles()
    levels()
    data_map()
    tables()
    delivery()


if __name__ == "__main__":
    main()
