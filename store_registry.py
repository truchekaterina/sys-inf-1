"""SQLite реестра: карточки, прошлые фразы, доставки, служебные справочники.

Ролей здесь нет. Кто имеет право смотреть карточку, решает фильтр.
"""

from __future__ import annotations

import sqlite3
import threading

from paths import REGISTRY_DB, REGISTRY_SQL


class RegistryStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()

    def reset(self) -> None:
        REGISTRY_DB.parent.mkdir(parents=True, exist_ok=True)
        if REGISTRY_DB.exists():
            REGISTRY_DB.unlink()
        script = REGISTRY_SQL.read_text(encoding="utf-8")
        con = self._connect()
        try:
            con.executescript(script)
        finally:
            con.close()

    def find_key(self, idempotency_key: str) -> dict | None:
        rows = self._read("SELECT * FROM cards WHERE idempotency_key = ?", (idempotency_key,))
        return self._full(rows[0]["card_id"]) if rows else None

    def insert_card(self, card: dict, attempt: int, http_status: int) -> dict:
        def run(con):
            cur = con.execute(
                """
                INSERT INTO cards (
                    created_at, user_id, question, topic, phrase, snippet,
                    code, level, idempotency_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    card["created_at"],
                    card["user_id"],
                    card["question"],
                    card["topic"],
                    card["phrase"],
                    card["snippet"],
                    card["code"],
                    card["level"],
                    card["idempotency_key"],
                ),
            )
            card_id = cur.lastrowid
            for item in card["prior_phrases"]:
                con.execute(
                    """
                    INSERT INTO card_prior_phrases (card_id, phrase, snippet, occurred_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (card_id, item["phrase"], item["snippet"], item["occurred_at"]),
                )
            _insert_delivery(con, card_id, attempt, card["created_at"], http_status)
            return card_id

        card_id = self._write(run)
        return self._full(card_id)

    def add_delivery(self, card_id: int, attempt: int, sent_at: str, http_status: int) -> None:
        def run(con):
            _insert_delivery(con, card_id, attempt, sent_at, http_status)

        self._write(run)

    def get_card(self, card_id: int) -> dict | None:
        rows = self._read("SELECT card_id FROM cards WHERE card_id = ?", (card_id,))
        return self._full(card_id) if rows else None

    def list_cards(self, user_id=None, topic=None, code=None, level=None, since=None, date_from=None, date_to=None):
        sql = "SELECT * FROM cards WHERE 1 = 1"
        args: list = []
        if user_id:
            sql += " AND user_id = ?"
            args.append(user_id)
        if topic:
            sql += " AND topic = ?"
            args.append(topic)
        if code:
            sql += " AND code = ?"
            args.append(code)
        if level:
            sql += " AND level = ?"
            args.append(level)
        if since:
            sql += " AND created_at >= ?"
            args.append(since)
        if date_from:
            sql += " AND substr(created_at, 1, 10) >= ?"
            args.append(date_from)
        if date_to:
            sql += " AND substr(created_at, 1, 10) <= ?"
            args.append(date_to)
        sql += " ORDER BY created_at, card_id"
        return [_brief(row) for row in self._read(sql, tuple(args))]

    def count_danger(self, user_id: str, topic: str, since: str) -> int:
        rows = self._read(
            """
            SELECT COUNT(*) AS n FROM cards
            WHERE user_id = ? AND topic = ? AND code = 'danger_phrase' AND created_at >= ?
            """,
            (user_id, topic, since),
        )
        return int(rows[0]["n"])

    def list_deliveries(self, card_id: int | None = None) -> list[dict]:
        if card_id is None:
            rows = self._read("SELECT * FROM deliveries ORDER BY sent_at, delivery_id")
        else:
            rows = self._read(
                "SELECT * FROM deliveries WHERE card_id = ? ORDER BY attempt, delivery_id",
                (card_id,),
            )
        return [_delivery(row) for row in rows]

    def list_codes(self) -> list[dict]:
        rows = self._read("SELECT code, title FROM codes ORDER BY code")
        return [{"code": row["code"], "title": row["title"]} for row in rows]

    def list_levels(self) -> list[dict]:
        rows = self._read("SELECT level, meaning FROM levels ORDER BY level")
        return [{"level": row["level"], "meaning": row["meaning"]} for row in rows]

    def _full(self, card_id: int) -> dict:
        row = self._read("SELECT * FROM cards WHERE card_id = ?", (card_id,))[0]
        priors = self._read(
            """
            SELECT phrase, snippet, occurred_at
            FROM card_prior_phrases
            WHERE card_id = ?
            ORDER BY occurred_at, id
            """,
            (card_id,),
        )
        item = _brief(row)
        item.update(
            {
                "question": row["question"],
                "snippet": row["snippet"],
                "prior_phrases": [
                    {"phrase": p["phrase"], "snippet": p["snippet"], "occurred_at": p["occurred_at"]}
                    for p in priors
                ],
            }
        )
        return item

    def _connect(self):
        con = sqlite3.connect(REGISTRY_DB)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        return con

    def _read(self, sql: str, args: tuple = ()):
        with self._lock:
            con = self._connect()
            try:
                return list(con.execute(sql, args))
            finally:
                con.close()

    def _write(self, fn):
        with self._lock:
            con = self._connect()
            try:
                result = fn(con)
                con.commit()
                return result
            except Exception:
                con.rollback()
                raise
            finally:
                con.close()


def _delivery(row) -> dict:
    return {
        "delivery_id": row["delivery_id"],
        "id": str(row["card_id"]),
        "attempt": row["attempt"],
        "sent_at": row["sent_at"],
        "http_status": row["http_status"],
        "reached": bool(row["reached"]),
    }


def _insert_delivery(con, card_id: int, attempt: int, sent_at: str, http_status: int) -> None:
    con.execute(
        """
        INSERT INTO deliveries (card_id, attempt, sent_at, http_status, reached)
        VALUES (?, ?, ?, ?, 1)
        """,
        (card_id, attempt, sent_at, http_status),
    )


def _brief(row) -> dict:
    return {
        "id": str(row["card_id"]),
        "card_id": row["card_id"],
        "created_at": row["created_at"],
        "user_id": row["user_id"],
        "topic": row["topic"],
        "phrase": row["phrase"],
        "snippet": row["snippet"],
        "code": row["code"],
        "level": row["level"],
        "delivered": True,
        "idempotency_key": row["idempotency_key"],
    }


REGISTRY = RegistryStore()
