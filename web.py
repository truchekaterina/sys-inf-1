"""Страницы браузера: главная и два Swagger. Файлы лежат в каталоге prototype."""

from __future__ import annotations

from urllib.parse import urlparse

from paths import DB_HOST, DB_PORT, OPENAPI_DIR, SWAGGER_DIR, UI_HOST, UI_PORT

FILES = {
    "/swagger/swagger-ui-bundle.js": (SWAGGER_DIR / "swagger-ui-bundle.js", "text/javascript; charset=utf-8"),
    "/swagger/swagger-ui.css": (SWAGGER_DIR / "swagger-ui.css", "text/css; charset=utf-8"),
    "/openapi-ui.yaml": (OPENAPI_DIR / "ui.yaml", "application/yaml; charset=utf-8"),
    "/openapi-db.yaml": (OPENAPI_DIR / "db.yaml", "application/yaml; charset=utf-8"),
}


def swagger_page(spec: str, title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <link rel="stylesheet" href="/swagger/swagger-ui.css">
  <style>
    html, body {{ background: #ffffff; }}
    body {{ margin: 0; }}
    .hint {{
      font-family: Segoe UI, sans-serif;
      background: #143d52;
      color: white;
      padding: 12px 20px;
      line-height: 1.45;
    }}
    .hint a {{ color: #9ad7ff; }}
  </style>
</head>
<body>
  <div class="hint">{title}. Кнопка <b>Authorize</b>, затем у запроса <b>Try it out</b> и <b>Execute</b>.
  <a href="/">На главную</a></div>
  <div id="swagger-ui"></div>
  <script src="/swagger/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({{
      url: "{spec}",
      dom_id: "#swagger-ui",
      docExpansion: "list",
      defaultModelsExpandDepth: -1,
      persistAuthorization: true,
      tryItOutEnabled: true
    }});
  </script>
</body>
</html>
"""


HOME = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Вывод → Реестр</title>
  <style>
    html, body {{ background: #ffffff; color: #1a1a1a; font-family: Segoe UI, sans-serif; }}
    body {{ max-width: 760px; margin: 32px auto; padding: 0 16px; line-height: 1.5; }}
    h1 {{ font-size: 28px; }}
    a.big {{ display: block; margin: 12px 0; padding: 16px 18px; background: #143d52; color: white; text-decoration: none; border-radius: 8px; font-size: 18px; }}
    a.big span {{ display: block; font-size: 14px; opacity: 0.85; }}
    code {{ background: #f2f2f2; padding: 1px 6px; }}
    ol li {{ margin: 6px 0; }}
  </style>
</head>
<body>
  <h1>ИС «Вывод → Реестр»</h1>
  <p>Окно PowerShell не закрывай. Пока оно открыто, работают эти страницы.</p>
  <a class="big" href="/docs">1. Запросы людей<span>сотрудник, специалист, аудитор, администратор. {UI_HOST}:{UI_PORT}</span></a>
  <a class="big" href="http://{DB_HOST}:{DB_PORT}/docs">2. Запросы реестра<span>карточки и доставки. {DB_HOST}:{DB_PORT}, ключ lab-service</span></a>
  <h2>Пароль у всех один: lab</h2>
  <p>На первой странице в <b>Authorize</b> вставь токен без слова Bearer:</p>
  <ul>
    <li><code>lab.employee</code> — чат, пользователь user_17</li>
    <li><code>lab.specialist</code> — журнал и карточка</li>
    <li><code>lab.auditor</code> — тот же журнал, только чтение</li>
    <li><code>lab.admin</code> — экран «Правила»</li>
  </ul>
  <h2>Порядок на первой странице</h2>
  <ol>
    <li><code>POST /auth/login</code> — <code>{{"login":"employee","password":"lab"}}</code>.</li>
    <li>Authorize → <code>lab.employee</code>.</li>
    <li><code>POST /chat/messages</code> с текстом без фраз списка. В ответе текст модели, в реестре пусто.</li>
    <li>Тот же запрос с документом, где есть «пароль». В чате одна строка «ответ отклонён».</li>
    <li>Authorize → <code>lab.specialist</code>, <code>GET /journal?user_id=user_17</code>.</li>
    <li>Открой карточку по id из списка. Там вопрос, фраза и кусок документа.</li>
    <li>Повтори опасный вопрос ещё два раза с темой «доступ». Третья карточка — уровень L4.</li>
    <li>На второй странице выключи приём: <code>PUT /stand/mode</code> с <code>{{"accept":false}}</code>. Новый опасный вопрос в чате снова отклонён, в журнале «запись не дошла».</li>
  </ol>
</body>
</html>
"""


DB_HOME = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Реестр, порт {DB_PORT}</title>
  <style>
    html, body {{ background: #ffffff; color: #1a1a1a; font-family: Segoe UI, sans-serif; }}
    body {{ max-width: 720px; margin: 32px auto; padding: 0 16px; line-height: 1.5; }}
    a {{ color: #143d52; }}
    code {{ background: #f2f2f2; padding: 1px 6px; }}
  </style>
</head>
<body>
  <h1>Это реестр карточек</h1>
  <p><a href="/docs">Открыть запросы реестра</a></p>
  <p>В Authorize вставь ключ <code>lab-service</code>.</p>
  <p>Чат и журнал открываются на <a href="http://{UI_HOST}:{UI_PORT}/">странице людей</a>.</p>
</body>
</html>
"""


def send_bytes(handler, body: bytes, content_type: str, status: int = 200) -> None:
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Service-Key")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
    handler.send_header("Connection", "close")
    handler.end_headers()
    handler.wfile.write(body)


def send_text(handler, text: str, content_type: str = "text/html; charset=utf-8") -> None:
    send_bytes(handler, text.encode("utf-8"), content_type)


def try_serve(handler, kind: str) -> bool:
    path = urlparse(handler.path).path
    if path in FILES:
        file_path, content_type = FILES[path]
        send_bytes(handler, file_path.read_bytes(), content_type)
        return True
    if path in ("/", ""):
        send_text(handler, HOME if kind == "ui" else DB_HOME)
        return True
    if path == "/docs":
        title = "Запросы людей" if kind == "ui" else "Запросы реестра"
        spec = "/openapi-ui.yaml" if kind == "ui" else "/openapi-db.yaml"
        send_text(handler, swagger_page(spec, title))
        return True
    return False
