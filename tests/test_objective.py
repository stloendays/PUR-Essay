import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pur_science import canonicalize, mdi_fraction, property_score, window_center
from pur_science.frontier import broad_margin, compute_frontier

ROOT = Path(__file__).resolve().parents[1]


def test_window_center_is_geometric_midpoint():
    assert abs(window_center([2.2, 5.5]) - math.sqrt(2.2 * 5.5)) < 1e-12
    with pytest.raises(ValueError):
        window_center([0.0, 1.0])


def test_mdi_fraction_definition():
    assert abs(mdi_fraction(55.30525) - 0.35610676393747154) < 1e-12
    with pytest.raises(ValueError):
        mdi_fraction(-1.0)


def test_property_score_reproduces_frozen_oracle_v2_scores():
    """The compact ORACLE V2 snapshot carries the frozen oracle_score; the objective must reproduce it exactly."""
    df = pd.read_csv(ROOT / "data" / "oracle_top30_compact.csv")
    cfg = json.loads((ROOT / "configs" / "oracle_v2.json").read_text(encoding="utf-8"))
    cfg["columns"] = {"candidate_id": "source_candidate_id", "blend": "blend", "nco_oh": "nco_oh", "mdi_parts": "mdi_parts",
                      "eta80": "simulated_eta_80c_pa_s", "eta120": "simulated_eta_120c_pa_s", "ratio": "simulated_ratio_80c_120c",
                      "domain_ratio": "simulated_domain_ratio"}
    table = canonicalize(df, cfg)
    score = property_score(table.frame, cfg)
    assert np.max(np.abs(score.to_numpy() - df["oracle_score"].to_numpy())) < 1e-12
    assert np.max(np.abs(table.frame["mdi_fraction"].to_numpy() - df["mdi_fraction_total"].to_numpy())) < 1e-12
    margin = broad_margin(table.frame, cfg)
    assert np.max(np.abs(margin.to_numpy() - df["broad_margin"].to_numpy())) < 1e-9
    # the snapshot is already in oracle order; the frozen tie-break chain must preserve it
    cfg["hard_constraints"].pop("require_chemistry_in_domain")
    cfg["hard_constraints"].pop("require_full_oracle_interval_inside_broad_window")
    f = compute_frontier(table, cfg)
    assert f.sort_values("nominal_rank")["cid"].tolist() == df["source_candidate_id"].tolist()


def test_property_score_matches_brute_force(toy_table, toy_config):
    from conftest import brute_force_property_score
    table = canonicalize(toy_table, toy_config)
    s = property_score(table.frame, toy_config)
    for i, row in toy_table.iterrows():
        assert abs(s.iloc[i] - brute_force_property_score(row)) < 1e-12


def test_canonicalize_parses_blend_components(toy_table, toy_config):
    table = canonicalize(toy_table, toy_config)
    assert table.components == ["X", "Y"]
    assert table.has_uncertainty and table.has_domain_ratio and table.has_in_domain
    row = table.row("T_0001")
    assert row["X"] == 50 and row["Y"] == 50
