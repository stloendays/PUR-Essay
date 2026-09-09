"""Shared fixtures.

`toy_table` is a small TEST FIXTURE with an invented response model. It exists only to
exercise the algorithms; it is not PUR_SIM_V1 and carries no scientific meaning.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]

C80, C120 = math.sqrt(2.2 * 5.5), math.sqrt(0.30 * 0.60)
K_X, K_Y = 36.0, 24.0  # MDI parts per unit NCO:OH for pure X / pure Y (X has the higher hydroxyl demand)
BLENDS = {"X:50+Y:50": (50, 50), "X:40+Y:60": (40, 60), "X:60+Y:40": (60, 40), "X:100": (100, 0), "Y:100": (0, 100)}
NCO_GRID = [round(1.5 + 0.1 * i, 1) for i in range(6)]


def make_toy_table() -> pd.DataFrame:
    rows = []
    i = 0
    for blend, (px, py) in BLENDS.items():
        fx = px / 100.0
        k = (px * K_X + py * K_Y) / 100.0
        for n in NCO_GRID:
            i += 1
            l80 = -0.5 * (n - 1.7) + 0.6 * (fx - 0.5)
            l120 = -0.4 * (n - 1.7) + 0.4 * (fx - 0.5)
            eta80 = C80 * 10 ** l80
            eta120 = C120 * 10 ** l120
            rows.append({
                "source_candidate_id": f"T_{i:04d}", "blend": blend, "nco_oh": n, "mdi_parts": k * n, "X": px, "Y": py,
                "eta80": eta80, "eta120": eta120, "ratio": eta80 / eta120,
                "domain_ratio": 1.5 if py == 100 or px == 100 else 0.5,
                "unc": 0.1 if px == 60 else 0.05,
                "in_domain": py != 100,
                "oracle_rank": 0, "gold_candidate_id": "leak",  # answer-bearing columns that must be stripped
            })
    return pd.DataFrame(rows)


def make_toy_config(robust: bool = True) -> dict:
    return {
        "workflow_id": "TEST_FIXTURE_V1", "benchmark_id": "TEST_RECOVER", "polyol_basis_parts": 100.0,
        "columns": {"candidate_id": "source_candidate_id", "blend": "blend", "nco_oh": "nco_oh", "mdi_parts": "mdi_parts",
                    "eta80": "eta80", "eta120": "eta120", "ratio": "ratio", "domain_ratio": "domain_ratio",
                    "uncertainty_radius": "unc", "chemistry_in_domain": "in_domain"},
        "hard_constraints": {"eta80_broad_pa_s": [0.85, 10.0], "eta120_broad_pa_s": [0.16, 0.80], "ratio_broad": [6.0, 13.0],
                             "eta80_preferred_pa_s": [2.2, 5.5], "eta120_preferred_pa_s": [0.30, 0.60], "ratio_preferred": [7.0, 9.5],
                             "nco_oh": [1.3, 3.0], "mdi_fraction_of_polyol_plus_mdi": [0.35, 0.49],
                             "require_chemistry_in_domain": True, "require_full_oracle_interval_inside_broad_window": True},
        "objective": {"space": "log10", "weights": {"eta80": 1.0, "eta120": 1.0, "ratio": 1.0},
                      "tie_break": ["higher_broad_margin", "lower_domain_ratio", "candidate_id_lexicographic"]},
        "robustness": {"enabled": robust, "method": "worst_case_interval", "require_interval_inside_preferred": True, "domain_ratio_max": 1.0},
        "backward": {"constraint": "mdi_fraction_min", "variable": "nco_oh"},
        "local_trends": {"response": "eta80"},
        "anonymization": {"component_columns": ["X", "Y"], "material_prefix": "Polyol", "seed": 7},
        "blind": {"drop_columns": ["oracle_rank"]},
        "required_outputs": ["property_winner", "constrained_winner", "robust_winner_or_explicit_abstention", "active_constraint", "backward_design", "local_trends"],
        "evaluation": {"backward_threshold_tolerance_nco_oh": 0.03, "top_k": [1, 3, 5]},
    }


@pytest.fixture
def toy_table() -> pd.DataFrame:
    return make_toy_table()


@pytest.fixture
def toy_config() -> dict:
    return make_toy_config()


@pytest.fixture
def toy_csv(tmp_path: Path, toy_table: pd.DataFrame) -> Path:
    p = tmp_path / "toy_candidates.csv"
    toy_table.to_csv(p, index=False)
    return p


@pytest.fixture
def design_space_table() -> pd.DataFrame:
    """Real 928-row design grid with placeholder responses (backward/reachability do not use responses)."""
    df = pd.read_csv(ROOT / "data" / "pur_sim_v1" / "design_space_928.csv")
    df["simulated_eta_80c_pa_s"] = 1.0
    df["simulated_eta_120c_pa_s"] = 1.0
    df["simulated_ratio_80c_120c"] = 1.0
    return df


@pytest.fixture
def frontier_config() -> dict:
    return json.loads((ROOT / "configs" / "frontier_v1.json").read_text(encoding="utf-8"))


def brute_force_property_score(row: pd.Series) -> float:
    cr = math.sqrt(7.0 * 9.5)
    return math.log10(row["eta80"] / C80) ** 2 + math.log10(row["eta120"] / C120) ** 2 + math.log10(row["ratio"] / cr) ** 2
