from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .conditions import Condition
from .data_access import BlindBundle

PROMPT_DIR = Path(__file__).resolve().parents[2] / "prompts"


def load_prompt(name: str, prompt_dir: str | Path | None = None) -> str:
    path = Path(prompt_dir or PROMPT_DIR) / name
    if not path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def compress_table(df: pd.DataFrame, config: dict[str, Any], *, sig: int = 5) -> str:
    """Compact CSV text of the admissible data for the direct-LLM baseline."""
    cols = config.get("columns", {})
    keep = [c for c in (cols.get("candidate_id"), cols.get("blend"), cols.get("nco_oh"), cols.get("mdi_parts"),
                        cols.get("eta80"), cols.get("eta120"), cols.get("ratio"), cols.get("domain_ratio"),
                        cols.get("uncertainty_radius"), cols.get("chemistry_in_domain")) if c and c in df.columns]
    out = df[keep].copy()
    for c in out.columns:
        if pd.api.types.is_float_dtype(out[c]):
            out[c] = out[c].map(lambda v: float(f"{v:.{sig}g}"))
    return out.to_csv(index=False)


def build_task_text(bundle: BlindBundle, condition: Condition, *, prompt_dir: str | Path | None = None) -> str:
    """Task prompt shared by every LLM condition; only optional blocks differ."""
    cfg = bundle.config
    template = load_prompt("recover_v1_task.txt", prompt_dir)
    public = {
        "benchmark_id": cfg.get("benchmark_id"),
        "polyol_basis_parts": cfg.get("polyol_basis_parts"),
        "columns": cfg.get("columns"),
        "hard_constraints": cfg.get("hard_constraints"),
        "objective": cfg.get("objective"),
        "robustness": cfg.get("robustness"),
        "backward": cfg.get("backward"),
        "local_trends": cfg.get("local_trends"),
        "required_outputs": bundle.task.get("required_outputs"),
    }
    text = template.replace("{{TASK_JSON}}", json.dumps(bundle.task, indent=2)).replace("{{CONFIG_JSON}}", json.dumps(public, indent=2))
    prov = bundle.task.get("provenance") if condition.include_provenance else None
    text = text.replace("{{PROVENANCE_BLOCK}}", ("Provenance and evidence boundary:\n" + json.dumps(prov, indent=2)) if prov else "")
    if condition.inline_data:
        csv_text = compress_table(bundle.candidates, cfg)
        text += "\n\nComplete admissible candidate table (CSV, all rows):\n```csv\n" + csv_text + "```\n"
        text += "\nNo tools are available. Reason from the table and the frozen definitions only, then return the JSON."
    else:
        text += "\n\nUse the deterministic tools; do not compute rankings mentally."
    return text
