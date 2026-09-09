from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def candidate_id_column(df_columns: list[str], configured: str | None = None) -> str:
    if configured and configured in df_columns:
        return configured
    for name in ("source_candidate_id", "candidate_id", "formulation_id"):
        if name in df_columns:
            return name
    raise KeyError("No candidate ID column found; configure columns.candidate_id explicitly.")
