from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWED = ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL", "OPENAI_PROVIDER")


def load_dotenv(path: str | Path | None = None) -> list[str]:
    """Load OPENAI_* variables from the repo-root .env into the process (never overriding
    values already set, never logging values). Returns the names that were loaded."""
    p = Path(path) if path else REPO_ROOT / ".env"
    loaded: list[str] = []
    if not p.is_file():
        return loaded
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key in ALLOWED and value and not os.getenv(key):
            os.environ[key] = value
            loaded.append(key)
    return loaded
