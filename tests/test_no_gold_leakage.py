import json
from pathlib import Path

import pytest

from pur_agent.blind_bundle import build_blind_bundle, verify_no_leakage
from pur_agent.data_access import AccessDenied, BlindBundle, BundleReader

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def bundle_dirs(tmp_path, toy_csv, toy_config):
    blind = tmp_path / "bench" / "blind"
    ev = tmp_path / "bench" / "evaluator_only"
    build_blind_bundle(toy_csv, toy_config, blind, ev, seed=7)
    return blind, ev


def test_bundle_passes_leakage_scan(bundle_dirs, toy_table):
    blind, ev = bundle_dirs
    gold_texts = [p.read_text(encoding="utf-8") for p in ev.glob("*.json")]
    v = verify_no_leakage(blind, toy_table["source_candidate_id"].tolist(), ["X", "Y"], gold_texts=gold_texts)
    assert v == [], v
    assert verify_no_leakage(ROOT / "prompts", gold_texts=gold_texts) == []


def test_public_config_has_no_expectations_or_mappings(bundle_dirs):
    blind, _ = bundle_dirs
    cfg = json.loads((blind / "benchmark_config.json").read_text())
    for key in ("gold", "anonymization", "blind", "expected_from_docs"):
        assert key not in cfg
    assert cfg["columns"]["candidate_id"] == "candidate_id"


def test_scan_fails_on_injected_gold(bundle_dirs):
    blind, ev = bundle_dirs
    (blind / "notes.json").write_text((ev / "gold_decision.json").read_text())
    gold_texts = [p.read_text(encoding="utf-8") for p in ev.glob("*.json")]
    v = verify_no_leakage(blind, gold_texts=gold_texts)
    assert any("byte-identical" in x for x in v) and any("forbidden token" in x or "source candidate id" in x for x in v)


def test_scan_fails_on_forbidden_tokens(tmp_path):
    d = tmp_path / "blind"; d.mkdir()
    (d / "task.json").write_text('{"hint": "the known winner is WO_INV_0420, oracle_rank 1"}')
    v = verify_no_leakage(d)
    assert any("known winner" in x for x in v) and any("WO_INV_0420" in x for x in v) and any("oracle_rank" in x for x in v)


def test_runtime_guard_refuses_evaluator_paths(bundle_dirs):
    blind, ev = bundle_dirs
    reader = BundleReader(blind)
    for probe in ("../evaluator_only/gold_decision.json", "../evaluator_only/gold_mapping.json", "gold_decision.json",
                  str(ev / "gold_decision.json"), "../../../results/oracle_v2/oracle_best.json", "candidates.csv/../../evaluator_only/gold_mapping.json"):
        with pytest.raises((AccessDenied, FileNotFoundError)):
            reader.resolve(probe)
    with pytest.raises(AccessDenied):
        BundleReader(ev)
    b = BlindBundle.load(blind)
    assert len(b.candidates) > 0 and "candidates.csv" in b.hashes


def test_gold_and_blind_gold_are_consistent(bundle_dirs):
    _, ev = bundle_dirs
    gold = json.loads((ev / "gold_decision.json").read_text())
    blind_gold = json.loads((ev / "gold_decision_blind.json").read_text())
    mapping = json.loads((ev / "gold_mapping.json").read_text())
    assert gold["gold_status"] == "GOLD"
    assert mapping["candidate_reverse"][blind_gold["robust_winner"]] == gold["robust_winner"]
    assert blind_gold["robust_winner"].startswith("Candidate_")
    assert blind_gold["local_trends"]["composition_axis"].startswith("Polyol_")
