-- Память фильтра. Это не реестр.
-- Реплика чата не содержит фразу, уровень и кусок документа.
-- Очередь хранит карточку, которую реестр не принял.
-- Журнал вызовов хранит адрес и код ответа, без текста документа и без токена.
--
-- Файл данных стенда: data/filter.db (SQLite).
-- При каждом запуске serve.py файл создаётся заново.

CREATE TABLE turns (
    turn_id      INTEGER PRIMARY KEY,                 -- номер реплики в чате
    created_at   TEXT    NOT NULL,                    -- время вопроса
    user_id      TEXT    NOT NULL,                    -- чей чат
    question     TEXT    NOT NULL,                    -- что спросил сотрудник
    topic        TEXT    NOT NULL,                    -- тема вопроса
    visible_text TEXT    NOT NULL                     -- ответ модели или «ответ отклонён»
);

CREATE INDEX ix_turns_user_time ON turns (user_id, created_at);

CREATE TABLE outbox (
    outbox_id       INTEGER PRIMARY KEY,              -- номер недоставленной карточки
    created_at      TEXT    NOT NULL,
    user_id         TEXT    NOT NULL,
    question        TEXT    NOT NULL,
    topic           TEXT    NOT NULL,
    phrase          TEXT    NOT NULL,
    snippet         TEXT    NOT NULL,
    code            TEXT    NOT NULL,
    level           TEXT    NOT NULL,
    idempotency_key TEXT    NOT NULL UNIQUE,
    prior_json      TEXT    NOT NULL,                 -- прошлые фразы для L4, JSON
    mark            TEXT    NOT NULL                  -- «запись не дошла»
);

CREATE INDEX ix_outbox_user_topic_time ON outbox (user_id, topic, created_at);

CREATE TABLE calls (
    call_id         INTEGER PRIMARY KEY,              -- номер вызова webhook
    sent_at         TEXT    NOT NULL,                 -- когда фильтр отправил карточку
    address         TEXT    NOT NULL,                 -- адрес без токена и без текста
    http_status     INTEGER NOT NULL,                 -- код ответа, 0 если связи не было
    attempt         INTEGER NOT NULL,                 -- 1 или 2
    idempotency_key TEXT    NOT NULL                  -- чтобы связать попытки одной карточки
);

CREATE INDEX ix_calls_key ON calls (idempotency_key);
