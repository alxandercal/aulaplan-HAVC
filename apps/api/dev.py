"""Punto de entrada del backend Flask (desarrollo local)."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def load_env(env_file: Path) -> None:
    """Carga apps/api/.env sin depender de python-dotenv."""
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env(BASE_DIR / ".env")

from src.http.app import create_app  # noqa: E402  (requiere el .env ya cargado)

app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", "8000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
