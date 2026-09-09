import pytest

from pur_science import canonicalize, solve_backward_threshold


def test_backward_threshold_on_real_design_grid(design_space_table, frontier_config):
    """PPG700:50+PPG1000:50 has k = 30.3875 MDI parts per unit NCO:OH -> floor 0.35 crossed at 1.7720."""
    table = canonicalize(design_space_table, frontier_config)
    sol = solve_backward_threshold(table, "WO_INV_0419", threshold=0.35)
    assert sol.manifold_is_linear
    assert abs(sol.manifold_slope_mdi_parts_per_nco - 30.3875) < 1e-9
    assert abs(sol.continuous_threshold - 1.7719836724361613) < 1e-9
    assert sol.candidate_value < 0.35
    assert sol.blend == "PPG1000:50+PPG700:50"


def test_backward_threshold_oracle_v2_blend(design_space_table, frontier_config):
    """ORACLE V2 story: 40/60 PPG400/PPG2000 at NCO 1.6 fails the floor, 1.7 is the first admissible point."""
    table = canonicalize(design_space_table, frontier_config)
    sol = solve_backward_threshold(table, "WO_INV_0578", threshold=0.35)
    assert 1.6 < sol.continuous_threshold < 1.7
    assert abs(table.row("WO_INV_0578")["mdi_fraction"] - 0.3423) < 1e-3
    assert table.row("WO_INV_0579")["mdi_fraction"] > 0.35


def test_every_blend_manifold_is_linear(design_space_table, frontier_config):
    table = canonicalize(design_space_table, frontier_config)
    for blend in table.frame["blend"].unique():
        cid = table.frame[table.frame["blend"] == blend].iloc[0]["cid"]
        assert solve_backward_threshold(table, cid, threshold=0.35).manifold_is_linear


def test_unknown_constraint_rejected(toy_table, toy_config):
    table = canonicalize(toy_table, toy_config)
    with pytest.raises(ValueError):
        solve_backward_threshold(table, "T_0001", threshold=0.35, constraint="something_else")
