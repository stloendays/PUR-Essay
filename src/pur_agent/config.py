from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

# Keys a benchmark config owns itself. Every other key of the referenced science definition is
# copied verbatim, so a new scientific block (e.g. `uncertainty`) can never be silently dropped.
BENCHMARK_OWNED_KEYS = frozenset({
    "benchmark_id", "science_definition_from", "note", "anonymization", "blind", "required_outputs",
    "evaluation", "secondary_benchmarks", "audit", "mode",
})


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def candidate_id_column(df_columns: list[str], configured: str | None = None) -> str:
    if configured and configured in df_columns:
        return configured
    for name in ("source_candidate_id", "candidate_id", "formulation_id"):
        if name in df_columns:
            return name
    raise KeyError("No candidate ID column found; configure columns.candidate_id explicitly.")


def load_benchmark_config(path: str | Path, *, repo_root: Path | None = None) -> dict[str, Any]:
    """Load a benchmark config and merge in the frozen science definition it points to.

    `configs/recover_v1.json` declares `science_definition_from`. Every scoring rule comes from
    that file: all of its keys except the benchmark-owned ones are copied, and the benchmark
    file may not override them. This keeps the benchmark identical to the frozen frontier.
    """
    cfg = load_json(path)
    ref = cfg.get("science_definition_from")
    if ref:
        root = repo_root or REPO_ROOT
        sci_path = Path(ref) if Path(ref).is_absolute() else root / ref
        sci = load_json(sci_path)
        for key, value in sci.items():
            if key in BENCHMARK_OWNED_KEYS:
                continue
            if key in cfg and cfg[key] != value:
                raise ValueError(f"Benchmark config {path} overrides frozen science key {key!r}; remove it from the benchmark file")
            cfg[key] = value
        cfg["science_definition_sha256"] = hashlib.sha256(json.dumps(sci, sort_keys=True).encode()).hexdigest()
    return cfg
