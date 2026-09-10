from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from pur_science import canonicalize, frontier_decision

from .anonymization import anonymize_candidate_table
from .data_access import sha256_file
from .logging_utils import sha256_json, utc_now

# Tokens that must never appear in any Agent-readable file (case-insensitive).
FORBIDDEN_TOKENS = (
    "gold_candidate_id", "oracle_rank", "oracle_score", "oracle_is_best", "gold_decision", "gold_mapping",
    "anonymous_mapping", "candidate_reverse", "material_reverse", "known winner", "final answer", "evaluator_only",
    "gold_status", "robust_order", "nominal_order", "property_order",
    "prospective_validation",
)
SOURCE_ID_PATTERN = re.compile(r"WO_INV_\d{4}", re.IGNORECASE)
PUBLIC_CONFIG_DROP = ("gold", "anonymization", "blind", "expected_from_docs")


def public_config(config: dict[str, Any]) -> dict[str, Any]:
    cfg = json.loads(json.dumps(config))
    for key in PUBLIC_CONFIG_DROP:
        cfg.pop(key, None)
    return cfg


def _gold_to_blind(gold: dict[str, Any], forward_c: dict[str, str], forward_m: dict[str, str]) -> dict[str, Any]:
    """Express the named gold decision in anonymous IDs (evaluator-side consistency check only)."""
    text = json.dumps(gold)
    for old, new in sorted(forward_c.items(), key=lambda kv: -len(kv[0])):
        text = text.replace(f'"{old}"', f'"{new}"')
    for old, new in sorted(forward_m.items(), key=lambda kv: -len(kv[0])):
        text = re.sub(rf"(?<![A-Za-z0-9_]){re.escape(old)}(?![A-Za-z0-9_])", new, text)
    return json.loads(text)


def build_blind_bundle(
    candidate_csv: str | Path,
    config: dict[str, Any],
    blind_dir: str | Path,
    evaluator_dir: str | Path,
    *,
    seed: int,
    task_provenance: dict[str, Any] | None = None,
    write_gold: bool = True,
) -> dict[str, Any]:
    """Write the Agent-readable blind bundle and the evaluator-only gold files.

    blind_dir/      candidates.csv, benchmark_config.json, task.json, manifest.json, provenance.json
    evaluator_dir/  gold_mapping.json, gold_decision.json (named), gold_decision_blind.json
    """
    blind_dir = Path(blind_dir); evaluator_dir = Path(evaluator_dir)
    blind_dir.mkdir(parents=True, exist_ok=True); evaluator_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(candidate_csv)
    anon = anonymize_candidate_table(df, config, seed=seed)
    pub = public_config(config)
    pub["primary_mode"] = "anonymous"
    src_id_col = config.get("columns", {}).get("candidate_id", "source_candidate_id")
    blind_table = anon.blind_table.rename(columns={src_id_col: "candidate_id"})
    pub.setdefault("columns", {})["candidate_id"] = "candidate_id"

    blind_csv = blind_dir / "candidates.csv"
    blind_table.to_csv(blind_csv, index=False)
    (blind_dir / "benchmark_config.json").write_text(json.dumps(pub, indent=2), encoding="utf-8")
    task = {
        "benchmark_id": config.get("benchmark_id", "PUR_RECOVER_V1"),
        "primary_mode": "anonymous",
        "instructions": "Recover the complete scientific decision chain using the frozen definitions. Do not guess.",
        "required_outputs": config.get("required_outputs", []),
        "provenance": task_provenance or {
            "candidate_space": "synthetic finite design grid (algorithm benchmark, not experimental evidence)",
            "response_origin": "deterministic simulated responses with a frozen log10 uncertainty interval per candidate",
            "constraints_origin": "literature-derived preferred/broad viscosity windows and chemistry/process bounds, frozen before this benchmark",
            "evidence_boundary": "no wet-lab result is included; identities are anonymized",
        },
    }
    (blind_dir / "task.json").write_text(json.dumps(task, indent=2), encoding="utf-8")

    src_hash = sha256_file(candidate_csv)
    manifest = {
        "benchmark_id": task["benchmark_id"],
        "built_utc": utc_now(),
        "seed": seed,
        "blind_candidate_sha256": sha256_file(blind_csv),
        "config_sha256": sha256_json(pub),
        "n_candidates": int(len(blind_table)),
    }
    (blind_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (blind_dir / "provenance.json").write_text(json.dumps({
        "source_table_sha256": src_hash,
        "note": "hash of the un-anonymized frozen source table; the table itself is evaluator-side",
    }, indent=2), encoding="utf-8")

    mapping = {
        "seed": seed,
        "candidate_reverse": anon.candidate_reverse,
        "material_reverse": anon.material_reverse,
        "candidate_forward": anon.candidate_forward,
        "material_forward": anon.material_forward,
        "source_candidate_sha256": src_hash,
        "blind_candidate_sha256": manifest["blind_candidate_sha256"],
    }
    (evaluator_dir / "gold_mapping.json").write_text(json.dumps(mapping, indent=2), encoding="utf-8")

    if write_gold:
        table = canonicalize(df, config)
        named = frontier_decision(table, config)
        gold = gold_from_frontier(named, config, src_hash)
        (evaluator_dir / "gold_decision.json").write_text(json.dumps(gold, indent=2), encoding="utf-8")
        blind_gold = _gold_to_blind(gold, anon.candidate_forward, anon.material_forward)
        (evaluator_dir / "gold_decision_blind.json").write_text(json.dumps(blind_gold, indent=2), encoding="utf-8")
        manifest["gold_sha256"] = sha256_json(gold)
        if named.get("robust_layer_frozen"):
            from .audit import audit_gold  # evaluator-side only
            agold = audit_gold(table, config)
            agold.update({"source_table_sha256": src_hash, "config_sha256": sha256_json(pub), "frozen_utc": utc_now()})
            (evaluator_dir / "gold_audit.json").write_text(json.dumps(agold, indent=2), encoding="utf-8")
            manifest["gold_audit_sha256"] = sha256_json(agold)
    return manifest


def gold_from_frontier(named: dict[str, Any], config: dict[str, Any], source_sha256: str, *, status: str = "GOLD") -> dict[str, Any]:
    """Evaluator-only gold record: decision fields, ordered rankings and per-candidate scores."""
    from pur_science.canonical import CID  # local import keeps module import light

    scores: dict[str, Any] = {}
    for layer, key in (("property_top", "property_score"), ("robust_top", "robust_score")):
        for row in named["rankings"].get(layer, []):
            scores.setdefault(row[CID], {})[key] = row.get(key)
    return {
        "gold_status": status,
        "workflow_id": config.get("workflow_id", "PUR_FRONTIER_V1"),
        "benchmark_id": config.get("benchmark_id", "PUR_RECOVER_V1"),
        "source_table_sha256": source_sha256,
        "config_sha256": sha256_json(public_config(config)),
        "frozen_utc": utc_now(),
        "n_candidates": named["n_candidates"],
        "n_feasible_nominal": named["n_feasible_nominal"],
        "n_feasible_robust": named["n_feasible_robust"],
        "robust_layer_frozen": named["robust_layer_frozen"],
        "property_winner": named["property_winner"],
        "constrained_winner": named["constrained_winner"],
        "robust_winner": named["robust_winner"],
        "decision_point": named["decision_point"],
        "active_constraint": named["active_constraint"],
        "backward_design": named["backward_design"],
        "local_trends": named["local_trends"],
        "rankings": named["rankings"],
        "scores": named.get("scores", scores),
    }


def verify_no_leakage(
    readable_dir: str | Path,
    original_candidate_ids: list[str] | None = None,
    original_materials: list[str] | None = None,
    *,
    gold_texts: list[str] | None = None,
    extra_tokens: list[str] | None = None,
) -> list[str]:
    """Scan every text file the Agent can read for forbidden content. Returns violations (empty = PASS)."""
    tokens = list(FORBIDDEN_TOKENS) + list(extra_tokens or []) + list(original_materials or [])
    ids = set(original_candidate_ids or [])
    violations: list[str] = []
    gold_hashes = {hashlib.sha256(t.encode()).hexdigest() for t in (gold_texts or [])}
    for path in sorted(Path(readable_dir).rglob("*")):
        if not path.is_file():
            continue
        if re.search(r"(gold|evaluator|mapping)", path.name, re.IGNORECASE):
            violations.append(f"{path}: evaluator-only file name inside Agent-readable directory")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if hashlib.sha256(text.encode()).hexdigest() in gold_hashes:
            violations.append(f"{path}: byte-identical copy of an evaluator gold file")
        low = text.lower()
        for token in tokens:
            if token and re.search(rf"(?<![a-z0-9_]){re.escape(token.lower())}(?![a-z0-9_])", low):
                violations.append(f"{path.name}: contains forbidden token {token!r}")
        for m in SOURCE_ID_PATTERN.findall(text):
            violations.append(f"{path.name}: contains source candidate id {m}")
            break
        for cid in ids:
            if cid.lower() in low:
                violations.append(f"{path.name}: contains source candidate id {cid}")
                break
    return violations
