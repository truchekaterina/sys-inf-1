-- Реестр отказов. Сюда попадают только карточки L3 и L4.
-- Код pass и список фраз здесь не хранятся: фразы живут в config/settings.txt,
-- а чистый ответ в реестр не уходит.
--
-- Файл данных стенда: data/registry.db (SQLite).
-- При каждом запуске serve.py файл создаётся заново.

PRAGMA foreign_keys = ON;

CREATE TABLE cards (
    card_id         INTEGER PRIMARY KEY,              -- номер карточки
    created_at      TEXT    NOT NULL,                 -- время отказа, UTC
    user_id         TEXT    NOT NULL,                 -- id сотрудника, например user_17
    question        TEXT    NOT NULL,                 -- вопрос в чате
    topic           TEXT    NOT NULL,                 -- тема, по ней копится правило C
    phrase          TEXT    NOT NULL,                 -- найденная фраза списка
    snippet         TEXT    NOT NULL,                 -- кусок документа вокруг фразы
    code            TEXT    NOT NULL,                 -- danger_phrase или topic_burst
    level           TEXT    NOT NULL,                 -- L3 или L4
    idempotency_key TEXT    NOT NULL UNIQUE,          -- повтор webhook не создаёт вторую карточку
    CONSTRAINT ck_cards_code CHECK (code IN ('danger_phrase', 'topic_burst')),
    CONSTRAINT ck_cards_level CHECK (level IN ('L3', 'L4')),
    CONSTRAINT ck_cards_pair CHECK (
        (code = 'danger_phrase' AND level = 'L3')
        OR (code = 'topic_burst' AND level = 'L4')
    )
);

CREATE INDEX ix_cards_user_topic_time ON cards (user_id, topic, created_at);
CREATE INDEX ix_cards_phrase ON cards (phrase);

CREATE TABLE card_prior_phrases (
    id          INTEGER PRIMARY KEY,                  -- номер строки истории
    card_id     INTEGER NOT NULL,                     -- карточка L4, к которой относится история
    phrase      TEXT    NOT NULL,                     -- прошлая фраза
    snippet     TEXT    NOT NULL,                     -- прошлый кусок документа
    occurred_at TEXT    NOT NULL,                     -- когда эта фраза уже находилась
    CONSTRAINT fk_prior_card
        FOREIGN KEY (card_id) REFERENCES cards (card_id)
);

CREATE INDEX ix_prior_card ON card_prior_phrases (card_id);

CREATE TABLE deliveries (
    delivery_id INTEGER PRIMARY KEY,                  -- номер попытки в журнале реестра
    card_id     INTEGER NOT NULL,                     -- какая карточка дошла
    attempt     INTEGER NOT NULL,                     -- 1 — первая отправка, 2 — повтор
    sent_at     TEXT    NOT NULL,                     -- время приёма
    http_status INTEGER NOT NULL,                     -- чем ответил реестр
    reached     INTEGER NOT NULL,                     -- 1 — запись легла в cards
    CONSTRAINT fk_delivery_card
        FOREIGN KEY (card_id) REFERENCES cards (card_id),
    CONSTRAINT ck_delivery_attempt CHECK (attempt >= 1),
    CONSTRAINT ck_delivery_reached CHECK (reached IN (0, 1))
);

CREATE INDEX ix_deliveries_card ON deliveries (card_id);

-- Служебные подписи кодов и уровней. Их задаёт стенд, роль их не меняет.
CREATE TABLE codes (
    code  TEXT PRIMARY KEY,                           -- pass, danger_phrase, topic_burst
    title TEXT NOT NULL                               -- что код значит
);

CREATE TABLE levels (
    level   TEXT PRIMARY KEY,                         -- L1, L3, L4
    meaning TEXT NOT NULL                             -- когда уровень ставится
);

INSERT INTO codes (code, title) VALUES
    ('pass', 'фразы списка нет, ответ выдан, в реестр не пишется'),
    ('danger_phrase', 'фраза найдена, выдача ответа запрещена'),
    ('topic_burst', 'по теме уже набралось N отказов за время T, выдача запрещена');

INSERT INTO levels (level, meaning) VALUES
    ('L1', 'фразы списка нет, ответ выдан'),
    ('L3', 'в документе найдена фраза списка'),
    ('L4', 'у этого id по теме уже N отказов за время T');
