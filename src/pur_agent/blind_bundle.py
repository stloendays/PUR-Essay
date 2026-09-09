from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from .anonymization import anonymize_candidate_table


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_blind_bundle(candidate_csv: str | Path, config: dict[str, Any], blind_dir: str | Path, evaluator_dir: str | Path, *, seed: int) -> dict[str, Any]:
    blind_dir = Path(blind_dir); evaluator_dir = Path(evaluator_dir)
    blind_dir.mkdir(parents=True, exist_ok=True); evaluator_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(candidate_csv)
    anon = anonymize_candidate_table(df, config, seed=seed)
    blind_csv = blind_dir / "candidates.csv"
    anon.blind_table.to_csv(blind_csv, index=False)
    public_config = json.loads(json.dumps(config))
    public_config.pop("gold", None)
    public_config.pop("anonymization", None)
    public_config.pop("blind", None)
    (blind_dir / "benchmark_config.json").write_text(json.dumps(public_config, indent=2), encoding="utf-8")
    task = {
        "benchmark_id": config.get("benchmark_id", "PUR_RECOVER_V1"),
        "primary_mode": "anonymous",
        "instructions": "Recover the complete scientific decision chain using deterministic tools. Do not guess.",
        "required_outputs": config.get("required_outputs", []),
    }
    (blind_dir / "task.json").write_text(json.dumps(task, indent=2), encoding="utf-8")
    mapping = {
        "seed": seed,
        "candidate_reverse": anon.candidate_reverse,
        "material_reverse": anon.material_reverse,
        "source_candidate_sha256": sha256_file(candidate_csv),
    }
    (evaluator_dir / "anonymous_mapping.json").write_text(json.dumps(mapping, indent=2), encoding="utf-8")
    manifest = {
        "blind_candidate_sha256": sha256_file(blind_csv),
        "config_sha256": hashlib.sha256(json.dumps(public_config, sort_keys=True).encode()).hexdigest(),
        "seed": seed,
    }
    (blind_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def verify_no_leakage(blind_dir: str | Path, original_candidate_ids: list[str] | None = None, original_materials: list[str] | None = None) -> list[str]:
    forbidden_tokens = ["gold_candidate_id", "oracle_rank", "oracle_score", "oracle_is_best", "gold_decision", "anonymous_mapping"]
    forbidden_tokens += original_candidate_ids or []
    forbidden_tokens += original_materials or []
    violations: list[str] = []
    for path in Path(blind_dir).rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        low = text.lower()
        for token in forbidden_tokens:
            if token and token.lower() in low:
                violations.append(f"{path.name}: contains forbidden token {token!r}")
    return violations
