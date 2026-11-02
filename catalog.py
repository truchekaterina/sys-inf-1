"""Демо-входы стенда. Пароль у всех один: lab. Это не учётные записи ОС."""

ACCOUNTS = {
    "employee": {"password": "lab", "role": "employee", "user_id": "user_17"},
    "specialist": {"password": "lab", "role": "specialist", "user_id": "spec_1"},
    "auditor": {"password": "lab", "role": "auditor", "user_id": "aud_1"},
    "admin": {"password": "lab", "role": "admin", "user_id": "adm_1"},
}

MODEL_ANSWER = "Ответ модели: см. документ."
REFUSAL_TEXT = "ответ отклонён"
OUTBOX_MARK = "запись не дошла"

TOKEN_PREFIX = "lab."
