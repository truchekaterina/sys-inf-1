"""Папки стенда. Корень — каталог prototype, не src."""

from pathlib import Path

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
CONFIG_FILE = ROOT / "config" / "settings.txt"
EXAMPLE_FILE = ROOT / "config" / "settings.example.txt"
DATA_DIR = ROOT / "data"
REGISTRY_DB = DATA_DIR / "registry.db"
FILTER_DB = DATA_DIR / "filter.db"
REGISTRY_SQL = ROOT / "sql" / "registry.sql"
FILTER_SQL = ROOT / "sql" / "filter.sql"
OPENAPI_DIR = ROOT / "openapi"
SWAGGER_DIR = ROOT / "swagger"

UI_HOST = "127.0.0.1"
DB_HOST = "127.0.0.2"
UI_PORT = 8091
DB_PORT = 8092
REGISTRY_ORIGIN = f"http://{DB_HOST}:{DB_PORT}"
SERVICE_HEADER = "X-Service-Key"
