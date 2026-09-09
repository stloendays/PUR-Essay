from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path
from typing import Any, Iterable

from .agent import run_once
from .conditions import get_condition
from .data_access import BlindBundle
from .evaluator import evaluate_run_record, load_gold
from .llm_client import make_client
from .logging_utils import write_run_record

BOOL_METRICS = (
    "complete_decision_recovery", "property_winner_recovery", "constrained_winner_recovery", "robust_winner_recovery",
    "active_constraint_recovery", "backward_threshold_recovery", "reachable_grid_recovery", "reachability_recovery",
    "nco_direction_recovery", "composition_direction_recovery", "top1_recovery", "top3_recovery", "top5_recovery",
    "abstained", "invalid_output",
)
NUM_METRICS = ("oracle_rank", "objective_regret", "hard_constraint_violation_rate", "backward_threshold_error",
               "explanation_fidelity", "tool_call_count", "input_tokens", "output_tokens", "api_calls", "latency_s")


def find_gold(blind_dir: str | Path, gold: str | None, mapping: str | None) -> tuple[Path | None, Path | None]:
    """Default evaluator-only locations next to the blind dir: <parent>/evaluator_only/."""
    ev = Path(blind_dir).resolve().parent / "evaluator_only"
    g = Path(gold) if gold else (ev / "gold_decision.json")
    m = Path(mapping) if mapping else (ev / "gold_mapping.json")
    return (g if g.is_file() else None), (m if m.is_file() else None)


def run_benchmark(
    *,
    blind_dir: str | Path,
    condition: str,
    provider: str,
    model: str,
    runs: int,
    out_dir: str | Path,
    gold: str | None = None,
    mapping: str | None = None,
    seed_base: int | None = None,
    max_rounds: int = 40,
    prompt_dir: str | Path | None = None,
    progress: bool = True,
) -> dict[str, Any]:
    bundle = BlindBundle.load(blind_dir)
    cond = get_condition(condition)
    client = make_client(provider, model, max_rounds=max_rounds) if cond.uses_llm else None
    gold_path, mapping_path = find_gold(blind_dir, gold, mapping)
    gold_obj = load_gold(gold_path) if gold_path else None
    mapping_obj = json.loads(Path(mapping_path).read_text(encoding="utf-8")) if mapping_path else None
    tol = float((bundle.config.get("evaluation") or {}).get("backward_threshold_tolerance_nco_oh", 0.03))
    top_k = tuple(int(k) for k in (bundle.config.get("evaluation") or {}).get("top_k", [1, 3, 5]))
    out = Path(out_dir); runs_dir = out / "runs"; runs_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for i in range(1, runs + 1):
        seed = (seed_base + i) if seed_base is not None else None
        rec = run_once(bundle, cond, client, run_id=f"run_{i:04d}", seed=seed, prompt_dir=prompt_dir)
        if gold_obj is not None:
            evaluate_run_record(rec, gold_obj, mapping_obj, backward_tolerance=tol, top_k=top_k)
        write_run_record(runs_dir / f"run_{i:04d}.json", rec)
        records.append(rec)
        if progress:
            ev = rec.get("evaluation") or {}
            print(f"[{cond.name}] run {i}/{runs} valid={rec.get('decision_valid')} complete={ev.get('complete_decision_recovery')} tools={rec.get('tool_call_count')}")
    summary = summarize_records(records, label={"condition": cond.name, "provider": provider if cond.uses_llm else "deterministic", "model": model if cond.uses_llm else "frontier_v1"})
    summary["gold_available"] = gold_obj is not None
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_summary_csv(out / "summary.csv", [summary])
    return summary


def summarize_records(records: Iterable[dict[str, Any]], *, label: dict[str, Any] | None = None) -> dict[str, Any]:
    recs = list(records)
    evals = [r.get("evaluation") for r in recs if r.get("evaluation")]
    summary: dict[str, Any] = {**(label or {}), "n_runs": len(recs), "n_evaluated": len(evals),
                               "n_valid_output": sum(bool(r.get("decision_valid")) for r in recs),
                               "n_errors": sum(bool(r.get("error")) for r in recs)}
    for m in BOOL_METRICS:
        vals = [bool(e.get(m)) for e in evals if m in e]
        summary[f"{m}_rate"] = (sum(vals) / len(vals)) if vals else None
    for m in NUM_METRICS:
        vals = [float(e[m]) for e in evals if e.get(m) is not None]
        summary[f"{m}_mean"] = statistics.fmean(vals) if vals else None
        summary[f"{m}_median"] = statistics.median(vals) if vals else None
    if not evals:  # tool/usage stats still available without gold
        summary["tool_call_count_mean"] = statistics.fmean([float(r.get("tool_call_count", 0)) for r in recs]) if recs else None
    return summary


def write_summary_csv(path: str | Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in keys})


def collect_runs(root: str | Path) -> list[dict[str, Any]]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(root).rglob("runs/run_*.json"))]


def summarize_tree(root: str | Path) -> list[dict[str, Any]]:
    """Group every run record under `root` by (condition, provider, model)."""
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for rec in collect_runs(root):
        key = (str(rec.get("condition")), str(rec.get("provider")), str(rec.get("model")))
        groups.setdefault(key, []).append(rec)
    return [summarize_records(v, label={"condition": k[0], "provider": k[1], "model": k[2]}) for k, v in sorted(groups.items())]
