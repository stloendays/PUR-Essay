from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SCIENCE_KEYS = ("polyol_basis_parts", "columns", "hard_constraints", "objective", "robustness", "backward", "local_trends", "design_space", "layers", "workflow_id")


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

    `configs/recover_v1.json` declares `science_definition_from`; every scoring rule comes
    from that file so the benchmark can never drift from the frozen frontier definition.
    """
    cfg = load_json(path)
    ref = cfg.get("science_definition_from")
    if ref:
        root = repo_root or REPO_ROOT
        sci = load_json(root / ref if not Path(ref).is_absolute() else ref)
        for key in SCIENCE_KEYS:
            if key in sci:
                cfg[key] = sci[key]
        cfg["science_definition_sha256"] = __import__("hashlib").sha256(json.dumps(sci, sort_keys=True).encode()).hexdigest()
        cfg.setdefault("expected_from_docs", sci.get("expected_from_docs"))
    return cfg
