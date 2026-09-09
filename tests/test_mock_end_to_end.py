import json
import os
from pathlib import Path

import pytest

from pur_agent.agent import run_once
from pur_agent.benchmark import run_benchmark, summarize_tree
from pur_agent.blind_bundle import build_blind_bundle
from pur_agent.conditions import CONDITIONS
from pur_agent.data_access import BlindBundle
from pur_agent.evaluator import evaluate_run_record, load_gold
from pur_agent.llm_client import MockLLMClient, make_client
from pur_agent.logging_utils import scrub_secrets, write_run_record


@pytest.fixture
def bench(tmp_path, toy_csv, toy_config):
    blind = tmp_path / "bench" / "blind"; ev = tmp_path / "bench" / "evaluator_only"
    build_blind_bundle(toy_csv, toy_config, blind, ev, seed=7)
    gold = load_gold(ev / "gold_decision.json")
    mapping = json.loads((ev / "gold_mapping.json").read_text())
    return BlindBundle.load(blind), gold, mapping, blind


def _run(bench, condition):
    bundle, gold, mapping, _ = bench
    cond = CONDITIONS[condition]
    rec = run_once(bundle, cond, MockLLMClient() if cond.uses_llm else None, seed=1)
    metrics = evaluate_run_record(rec, gold, mapping)
    return rec, metrics


def test_oracle_condition_recovers_gold_through_anonymization(bench):
    rec, m = _run(bench, "oracle")
    assert rec["decision_valid"] and m["complete_decision_recovery"] is True
    assert rec["final_json"]["robust_winner"].startswith("Candidate_")


def test_mock_pur_agent_recovers_complete_decision(bench):
    rec, m = _run(bench, "pur_agent")
    assert rec["decision_valid"] and rec["error"] is None
    assert rec["strategy_check"]["can_finalize"] is True
    assert m["complete_decision_recovery"] is True, m
    assert m["tool_call_count"] >= 9 and rec["provider"] == "mock"
    names = [t["tool"] for t in rec["tool_trace"]]
    assert names[0] == "dataset_summary" and "rank_robust" in names and "solve_backward_threshold" in names


def test_direct_llm_mock_is_an_honest_negative(bench):
    rec, m = _run(bench, "direct_llm")
    assert rec["decision_valid"] and m["abstained"] and not m["complete_decision_recovery"]
    assert rec["tool_call_count"] == 0


def test_ablation_without_backward_tools_loses_backward_fields(bench):
    rec, m = _run(bench, "pur_agent_no_backward")
    assert "solve_backward_threshold" not in rec["tools_available"]
    assert m["robust_winner_recovery"] and not m["backward_threshold_recovery"] and not m["complete_decision_recovery"]
    assert rec["strategy_check"]["can_finalize"] is True  # ablated tools are not required


def test_ablation_without_constraint_checker(bench):
    rec, m = _run(bench, "pur_agent_no_constraint_checker")
    assert not m["constrained_winner_recovery"] and not m["complete_decision_recovery"]


def test_robust_not_frozen_makes_mock_abstain_on_robust(tmp_path, toy_csv, toy_config):
    toy_config["robustness"]["enabled"] = False
    blind = tmp_path / "b2" / "blind"; ev = tmp_path / "b2" / "evaluator_only"
    build_blind_bundle(toy_csv, toy_config, blind, ev, seed=7)
    bundle = BlindBundle.load(blind)
    rec = run_once(bundle, CONDITIONS["pur_agent"], MockLLMClient())
    assert rec["final_json"]["robust_winner"] is None and rec["final_json"]["robust_abstention_reason"]
    m = evaluate_run_record(rec, load_gold(ev / "gold_decision.json"), json.loads((ev / "gold_mapping.json").read_text()))
    assert m["complete_decision_recovery"] is True and m["decision_layer_scored"] == "constrained_winner"


def test_benchmark_loop_writes_records_and_summary(bench, tmp_path):
    _, _, _, blind = bench
    out = tmp_path / "results" / "pur_agent" / "mock"
    s = run_benchmark(blind_dir=blind, condition="pur_agent", provider="mock", model="mock", runs=3, out_dir=out, seed_base=100, progress=False)
    assert s["n_runs"] == 3 and s["complete_decision_recovery_rate"] == 1.0 and s["gold_available"]
    files = sorted((out / "runs").glob("run_*.json"))
    assert len(files) == 3 and (out / "summary.csv").is_file()
    rec = json.loads(files[0].read_text())
    for key in ("run_id", "timestamp_utc", "model", "provider", "benchmark_id", "prompt_sha256", "data_sha256", "config_sha256",
                "anonymization_seed", "llm_seed", "tool_trace", "final_json", "usage", "api_response_ids", "latency_s", "evaluation"):
        assert key in rec
    assert rec["llm_seed"] == 101
    tree = summarize_tree(tmp_path / "results")
    assert tree[0]["condition"] == "pur_agent" and tree[0]["n_runs"] == 3


def test_run_records_never_contain_api_keys(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-1234567890abcdef")
    rec = {"raw_final_text": "key was sk-test-1234567890abcdef", "nested": {"x": ["sk-test-1234567890abcdef"]}}
    p = write_run_record(tmp_path / "r.json", rec)
    text = p.read_text()
    assert "sk-test-1234567890abcdef" not in text and "[REDACTED_API_KEY]" in text
    assert scrub_secrets("nothing here") == "nothing here"


def test_openai_clients_require_env_only(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        make_client("responses", "some-model")
    with pytest.raises(RuntimeError):
        make_client("chat", "some-model")
    assert make_client("mock", "").provider == "mock"
