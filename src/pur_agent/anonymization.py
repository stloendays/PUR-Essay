from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Any

import pandas as pd

from .config import candidate_id_column


@dataclass(frozen=True)
class AnonymizationResult:
    blind_table: pd.DataFrame
    candidate_forward: dict[str, str]
    candidate_reverse: dict[str, str]
    material_forward: dict[str, str]
    material_reverse: dict[str, str]


def _stable_seed(seed: int, label: str) -> int:
    digest = hashlib.sha256(f"{seed}:{label}".encode()).hexdigest()
    return int(digest[:16], 16)


def anonymize_candidate_table(df: pd.DataFrame, config: dict[str, Any], seed: int = 20260909) -> AnonymizationResult:
    out = df.copy()
    cols = config.get("columns", {})
    id_col = candidate_id_column(list(out.columns), cols.get("candidate_id"))

    original_ids = sorted(out[id_col].astype(str).unique())
    shuffled = original_ids[:]
    random.Random(_stable_seed(seed, "candidate")).shuffle(shuffled)
    candidate_forward = {old: f"Candidate_{i+1:04d}" for i, old in enumerate(shuffled)}
    candidate_reverse = {v: k for k, v in candidate_forward.items()}
    out[id_col] = out[id_col].astype(str).map(candidate_forward)

    component_cols = [x for x in config.get("anonymization", {}).get("component_columns", []) if x in out.columns]
    shuffled_components = component_cols[:]
    random.Random(_stable_seed(seed, "material")).shuffle(shuffled_components)
    alphabet = [chr(ord("A") + i) for i in range(26)]
    material_forward = {old: f"Material_{alphabet[i]}" for i, old in enumerate(shuffled_components)}
    material_reverse = {v: k for k, v in material_forward.items()}
    out = out.rename(columns={old: f"{new}_parts" for old, new in material_forward.items()})

    blend_col = cols.get("blend")
    if blend_col and blend_col in out.columns:
        def rewrite_blend(value: Any) -> str:
            text = str(value)
            for old, new in sorted(material_forward.items(), key=lambda kv: -len(kv[0])):
                text = text.replace(old, new)
            return text
        out[blend_col] = out[blend_col].map(rewrite_blend)

    forbidden = set(config.get("blind", {}).get("drop_columns", []))
    forbidden |= {c for c in out.columns if c.lower().startswith("gold_")}
    forbidden |= {c for c in out.columns if c.lower() in {"oracle_rank", "oracle_score", "oracle_is_best", "best_candidate"}}
    out = out.drop(columns=[c for c in forbidden if c in out.columns])
    return AnonymizationResult(out, candidate_forward, candidate_reverse, material_forward, material_reverse)
