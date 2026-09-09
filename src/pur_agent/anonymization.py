from __future__ import annotations

import hashlib
import random
import re
from dataclasses import dataclass
from typing import Any

import pandas as pd

from .config import candidate_id_column

# Columns whose names match this pattern never enter a blind table, whatever the config says.
AUTO_DROP_PATTERN = re.compile(r"(oracle|gold|rank|score|is_best|winner|nearest_training|formulation_id|source_url|locator)", re.IGNORECASE)


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
    """Deterministic, seed-fixed anonymisation of candidate IDs and material names.

    - candidate IDs -> Candidate_0001 ... in a seeded random permutation;
    - component columns (and their occurrences in blend strings) -> <prefix>_A ... in a seeded permutation;
    - answer-bearing columns are dropped.
    """
    out = df.copy()
    cols = config.get("columns", {})
    anon_cfg = config.get("anonymization", {})
    id_col = candidate_id_column(list(out.columns), cols.get("candidate_id"))

    original_ids = sorted(out[id_col].astype(str).unique())
    shuffled = original_ids[:]
    random.Random(_stable_seed(seed, "candidate")).shuffle(shuffled)
    candidate_forward = {old: f"Candidate_{i + 1:04d}" for i, old in enumerate(shuffled)}
    candidate_reverse = {v: k for k, v in candidate_forward.items()}
    out[id_col] = out[id_col].astype(str).map(candidate_forward)

    prefix = anon_cfg.get("material_prefix", "Polyol")
    component_cols = list(anon_cfg.get("component_columns", []))
    blend_col = cols.get("blend")
    if blend_col and blend_col in out.columns:
        for text in out[blend_col].astype(str):
            for token in text.split("+"):
                name = token.split(":")[0].strip()
                if name and name not in component_cols:
                    component_cols.append(name)
    component_cols = sorted(set(component_cols))
    shuffled_components = component_cols[:]
    random.Random(_stable_seed(seed, "material")).shuffle(shuffled_components)
    alphabet = [chr(ord("A") + i) for i in range(26)]
    if len(shuffled_components) > len(alphabet):
        raise ValueError("More than 26 components are not supported by the letter scheme")
    material_forward = {old: f"{prefix}_{alphabet[i]}" for i, old in enumerate(shuffled_components)}
    material_reverse = {v: k for k, v in material_forward.items()}
    out = out.rename(columns={old: f"{new}_parts" for old, new in material_forward.items() if old in out.columns})

    if blend_col and blend_col in out.columns:
        def rewrite_blend(value: Any) -> str:
            text = str(value)
            for old, new in sorted(material_forward.items(), key=lambda kv: -len(kv[0])):
                text = re.sub(rf"(?<![A-Za-z0-9_]){re.escape(old)}(?![A-Za-z0-9_])", new, text)
            return text
        out[blend_col] = out[blend_col].map(rewrite_blend)

    forbidden = set(config.get("blind", {}).get("drop_columns", []))
    forbidden |= {c for c in out.columns if c != id_col and AUTO_DROP_PATTERN.search(c)}
    out = out.drop(columns=[c for c in forbidden if c in out.columns])
    out = out.sort_values(id_col, kind="mergesort").reset_index(drop=True)
    return AnonymizationResult(out, candidate_forward, candidate_reverse, material_forward, material_reverse)
