import copy
import math

import pandas as pd

from pur_science import canonicalize
from pur_science.objective import robust_checks, uncertainty_radius_multipliers, worst_case_property_score


def _config():
    return {
        "polyol_basis_parts": 100.0,
        "columns": {
            "candidate_id": "source_candidate_id",
            "blend": "blend",
            "nco_oh": "nco_oh",
            "mdi_parts": "mdi_parts",
            "eta80": "eta80",
            "eta120": "eta120",
            "ratio": "ratio",
            "domain_ratio": "domain_ratio",
            "uncertainty_radius": "unc",
            "chemistry_in_domain": "in_domain",
        },
        "hard_constraints": {
            "eta80_broad_pa_s": [0.85, 10.0],
            "eta120_broad_pa_s": [0.16, 0.80],
            "ratio_broad": [6.0, 13.0],
            "eta80_preferred_pa_s": [2.2, 5.5],
            "eta120_preferred_pa_s": [0.30, 0.60],
            "ratio_preferred": [7.0, 9.5],
            "nco_oh": [1.3, 3.0],
            "mdi_fraction_of_polyol_plus_mdi": [0.35, 0.49],
            "require_chemistry_in_domain": True,
        },
        "objective": {"weights": {"eta80": 1.0, "eta120": 1.0, "ratio": 1.0}},
        "uncertainty": {"log10_radius_multiplier": {"eta80": 1.0, "eta120": 1.0, "ratio": 2.0}},
        "robustness": {
            "enabled": True,
            "method": "worst_case_interval",
            "require_interval_inside_broad": True,
            "require_interval_inside_preferred": False,
            "domain_ratio_max": 1.0,
        },
    }


def _row():
    return pd.DataFrame([{
        "source_candidate_id": "C1",
        "blend": "X:50+Y:50",
        "nco_oh": 1.8,
        "mdi_parts": 55.0,
        "eta80": 3.4,
        "eta120": 0.4,
        "ratio": 8.2,
        "domain_ratio": 0.5,
        "unc": 0.05,
        "in_domain": True,
    }])


def test_frontier_v1_uses_double_log_radius_for_ratio():
    cfg = _config()
    table = canonicalize(_row(), cfg)
    mult = uncertainty_radius_multipliers(cfg)
    assert mult == {"eta80": 1.0, "eta120": 1.0, "ratio": 2.0}

    score = float(worst_case_property_score(table.frame, cfg).iloc[0])
    centers = {
        "eta80": math.sqrt(2.2 * 5.5),
        "eta120": math.sqrt(0.30 * 0.60),
        "ratio": math.sqrt(7.0 * 9.5),
    }
    expected = (
        (abs(math.log10(3.4 / centers["eta80"])) + 0.05) ** 2
        + (abs(math.log10(0.4 / centers["eta120"])) + 0.05) ** 2
        + (abs(math.log10(8.2 / centers["ratio"])) + 0.10) ** 2
    )
    assert abs(score - expected) < 1e-14


def test_broad_interval_is_robust_admissible_without_preferred_certification():
    cfg = _config()
    table = canonicalize(_row(), cfg)
    checks = robust_checks(table, cfg)
    assert bool(checks.iloc[0]["interval_inside_broad"])
    assert bool(checks.iloc[0]["domain_ratio_max"])

    stricter = copy.deepcopy(cfg)
    stricter["robustness"]["require_interval_inside_preferred"] = True
    checks_strict = robust_checks(canonicalize(_row(), stricter), stricter)
    assert not bool(checks_strict.iloc[0]["interval_inside_preferred"])


def test_legacy_configs_without_multipliers_keep_all_ones_behavior():
    cfg = _config()
    cfg.pop("uncertainty")
    assert uncertainty_radius_multipliers(cfg) == {"eta80": 1.0, "eta120": 1.0, "ratio": 1.0}
