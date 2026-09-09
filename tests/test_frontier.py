import math

import numpy as np
import pytest

from pur_science import canonicalize, compute_frontier, frontier_decision
from pur_science.objective import robust_checks

from conftest import brute_force_property_score


def _feasible_nominal(row):
    hc = {"eta80": (0.85, 10.0, 2.2, 5.5), "eta120": (0.16, 0.80, 0.30, 0.60), "ratio": (6.0, 13.0, 7.0, 9.5)}
    ok = 1.3 <= row["nco_oh"] <= 3.0 and 0.35 <= row["mdi_parts"] / (100 + row["mdi_parts"]) <= 0.49 and bool(row["in_domain"])
    for k, (blo, bhi, plo, phi) in hc.items():
        v = row[k]
        ok &= blo <= v <= bhi and plo <= v <= phi
        ok &= (math.log10(v) - row["unc"]) >= math.log10(blo) and (math.log10(v) + row["unc"]) <= math.log10(bhi)
    return ok


def _feasible_robust(row):
    if not _feasible_nominal(row) or row["domain_ratio"] > 1.0:
        return False
    for k, (plo, phi) in {"eta80": (2.2, 5.5), "eta120": (0.30, 0.60), "ratio": (7.0, 9.5)}.items():
        if (math.log10(row[k]) - row["unc"]) < math.log10(plo) or (math.log10(row[k]) + row["unc"]) > math.log10(phi):
            return False
    return True


def _robust_score(row):
    c = {"eta80": math.sqrt(2.2 * 5.5), "eta120": math.sqrt(0.3 * 0.6), "ratio": math.sqrt(7.0 * 9.5)}
    return sum((abs(math.log10(row[k] / c[k])) + row["unc"]) ** 2 for k in c)


def test_layers_match_brute_force(toy_table, toy_config):
    table = canonicalize(toy_table, toy_config)
    f = compute_frontier(table, toy_config)
    bf = toy_table.copy()
    bf["J"] = bf.apply(brute_force_property_score, axis=1)
    bf["feasN"] = bf.apply(_feasible_nominal, axis=1)
    bf["feasR"] = bf.apply(_feasible_robust, axis=1)
    bf["JR"] = bf.apply(_robust_score, axis=1)
    assert f["feasible_nominal"].tolist() == bf["feasN"].tolist()
    assert f["feasible_robust"].tolist() == bf["feasR"].tolist()
    assert np.allclose(f["robust_score"], bf["JR"])
    d = frontier_decision(table, toy_config)
    assert d["property_winner"] == bf.sort_values(["J", "source_candidate_id"]).iloc[0]["source_candidate_id"]
    assert d["constrained_winner"] == bf[bf.feasN].sort_values(["J", "source_candidate_id"]).iloc[0]["source_candidate_id"]
    assert d["robust_winner"] == bf[bf.feasR].sort_values(["JR", "source_candidate_id"]).iloc[0]["source_candidate_id"]


def test_decision_frontier_structure(toy_table, toy_config):
    table = canonicalize(toy_table, toy_config)
    d = frontier_decision(table, toy_config)
    # property optimum sits at the objective center (50/50, NCO 1.7) but fails the MDI floor
    pw = table.row(d["property_winner"])
    assert pw["blend"] == "X:50+Y:50" and abs(pw["nco_oh"] - 1.7) < 1e-9
    assert d["active_constraint"]["name"] == "mdi_fraction"
    assert d["active_constraint"]["threshold"] == 0.35
    assert d["active_constraint"]["candidate_value"] < 0.35
    # backward: k = 30 for 50/50 -> n* = 0.35/0.65*100/30
    assert abs(d["backward_design"]["continuous_threshold"] - 0.35 / 0.65 * 100 / 30) < 1e-9
    assert d["backward_design"]["nearest_reachable_grid_value"] == 1.8
    assert d["backward_design"]["reachable"] is True
    # three different winners -> genuine ranking inversion in the fixture
    assert d["property_winner"] != d["constrained_winner"]
    assert d["robust_winner"] != d["constrained_winner"]
    rw = table.row(d["robust_winner"])
    assert rw["blend"] == "X:50+Y:50" and abs(rw["nco_oh"] - 1.8) < 1e-9
    # local trends at the robust winner: eta80 falls with NCO, rises with the higher-demand component X
    assert d["local_trends"]["nco_direction"] == "decrease"
    assert d["local_trends"]["composition_axis"] == "X"
    assert d["local_trends"]["composition_direction"] == "increase"
    assert d["scores"][d["robust_winner"]]["feasible_robust"] is True
    assert d["rankings"]["robust_order"][0] == d["robust_winner"]


def test_robust_layer_refuses_when_not_frozen(toy_table, toy_config):
    toy_config["robustness"]["enabled"] = False
    table = canonicalize(toy_table, toy_config)
    with pytest.raises(RuntimeError):
        robust_checks(table, toy_config)
    d = frontier_decision(table, toy_config)
    assert d["robust_winner"] is None and d["robust_layer_frozen"] is False
    assert d["decision_point"] == d["constrained_winner"]


def test_missing_uncertainty_column_is_an_explicit_error(toy_table, toy_config):
    toy_table = toy_table.drop(columns=["unc"])
    toy_config["columns"].pop("uncertainty_radius")
    table = canonicalize(toy_table, toy_config)
    with pytest.raises(KeyError):
        compute_frontier(table, toy_config)
