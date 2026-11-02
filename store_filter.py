"""SQLite фильтра: реплики чата, недоставленные карточки, журнал вызовов."""

from __future__ import annotations

import json
import sqlite3
import threading

from paths import FILTER_DB, FILTER_SQL


class FilterStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()

    def reset(self) -> None:
        FILTER_DB.parent.mkdir(parents=True, exist_ok=True)
        if FILTER_DB.exists():
            FILTER_DB.unlink()
        script = FILTER_SQL.read_text(encoding="utf-8")
        con = self._connect()
        try:
            con.executescript(script)
        finally:
            con.close()

    def add_turn(self, created_at: str, user_id: str, question: str, topic: str, visible_text: str) -> dict:
        def run(con):
            cur = con.execute(
                """
                INSERT INTO turns (created_at, user_id, question, topic, visible_text)
                VALUES (?, ?, ?, ?, ?)
                """,
                (created_at, user_id, question, topic, visible_text),
            )
            return _turn(con.execute("SELECT * FROM turns WHERE turn_id = ?", (cur.lastrowid,)).fetchone())

        return self._write(run)

    def list_turns(self, user_id: str) -> list[dict]:
        rows = self._read(
            "SELECT * FROM turns WHERE user_id = ? ORDER BY created_at, turn_id",
            (user_id,),
        )
        return [_turn(row) for row in rows]

    def get_turn(self, turn_id: int, user_id: str) -> dict | None:
        rows = self._read(
            "SELECT * FROM turns WHERE turn_id = ? AND user_id = ?",
            (turn_id, user_id),
        )
        return _turn(rows[0]) if rows else None

    def add_outbox(self, card: dict, mark: str) -> dict:
        def run(con):
            cur = con.execute(
                """
                INSERT INTO outbox (
                    created_at, user_id, question, topic, phrase, snippet,
                    code, level, idempotency_key, prior_json, mark
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    json.dumps(card["prior_phrases"], ensure_ascii=False),
                    mark,
                ),
            )
            row = con.execute("SELECT * FROM outbox WHERE outbox_id = ?", (cur.lastrowid,)).fetchone()
            return _outbox(row)

        return self._write(run)

    def list_outbox(self) -> list[dict]:
        return [_outbox(row) for row in self._read("SELECT * FROM outbox ORDER BY created_at, outbox_id")]

    def get_outbox(self, outbox_id: int) -> dict | None:
        rows = self._read("SELECT * FROM outbox WHERE outbox_id = ?", (outbox_id,))
        return _outbox(rows[0]) if rows else None

    def count_danger(self, user_id: str, topic: str, since: str) -> int:
        rows = self._read(
            """
            SELECT COUNT(*) AS n FROM outbox
            WHERE user_id = ? AND topic = ? AND code = 'danger_phrase' AND created_at >= ?
            """,
            (user_id, topic, since),
        )
        return int(rows[0]["n"])

    def danger_rows(self, user_id: str, topic: str, since: str) -> list[dict]:
        rows = self._read(
            """
            SELECT * FROM outbox
            WHERE user_id = ? AND topic = ? AND code = 'danger_phrase' AND created_at >= ?
            ORDER BY created_at, outbox_id
            """,
            (user_id, topic, since),
        )
        return [_outbox(row) for row in rows]

    def add_call(self, sent_at: str, address: str, http_status: int, attempt: int, idempotency_key: str) -> None:
        def run(con):
            con.execute(
                """
                INSERT INTO calls (sent_at, address, http_status, attempt, idempotency_key)
                VALUES (?, ?, ?, ?, ?)
                """,
                (sent_at, address, http_status, attempt, idempotency_key),
            )

        self._write(run)

    def list_calls(self) -> list[dict]:
        rows = self._read("SELECT * FROM calls ORDER BY sent_at, call_id")
        return [_call(row, public=True) for row in rows]

    def calls_for(self, idempotency_key: str) -> list[dict]:
        rows = self._read(
            "SELECT * FROM calls WHERE idempotency_key = ? ORDER BY attempt, call_id",
            (idempotency_key,),
        )
        return [_call(row, public=False) for row in rows]

    def _connect(self):
        con = sqlite3.connect(FILTER_DB)
        con.row_factory = sqlite3.Row
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


def _turn(row) -> dict:
    return {
        "turn_id": row["turn_id"],
        "created_at": row["created_at"],
        "user_id": row["user_id"],
        "question": row["question"],
        "topic": row["topic"],
        "visible_text": row["visible_text"],
    }


def _outbox(row) -> dict:
    return {
        "outbox_id": row["outbox_id"],
        "id": f"out-{row['outbox_id']}",
        "created_at": row["created_at"],
        "user_id": row["user_id"],
        "question": row["question"],
        "topic": row["topic"],
        "phrase": row["phrase"],
        "snippet": row["snippet"],
        "code": row["code"],
        "level": row["level"],
        "idempotency_key": row["idempotency_key"],
        "prior_phrases": json.loads(row["prior_json"]),
        "mark": row["mark"],
        "delivered": False,
    }


def _call(row, public: bool) -> dict:
    item = {
        "call_id": row["call_id"],
        "sent_at": row["sent_at"],
        "address": row["address"],
        "http_status": row["http_status"],
        "attempt": row["attempt"],
    }
    if not public:
        item["idempotency_key"] = row["idempotency_key"]
    return item


FILTER = FilterStore()
