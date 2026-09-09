from pur_science import canonicalize, check_reachability, solve_backward_threshold


def test_reachable_grid_point_on_real_grid(design_space_table, frontier_config):
    table = canonicalize(design_space_table, frontier_config)
    sol = solve_backward_threshold(table, "WO_INV_0419", threshold=0.35)
    r = check_reachability(table, sol)
    assert r.reachable is True
    assert r.nearest_reachable_grid_value == 1.8
    assert r.nearest_reachable_candidate_id == "WO_INV_0420"
    assert r.grid_values[0] == 1.5 and r.grid_values[-1] == 3.0 and len(r.grid_values) == 16


def test_unreachable_when_threshold_beyond_grid(design_space_table, frontier_config):
    table = canonicalize(design_space_table, frontier_config)
    sol = solve_backward_threshold(table, "WO_INV_0001", threshold=0.60)  # pure PPG1000 never reaches 60 wt% on this grid
    r = check_reachability(table, sol)
    assert r.reachable is False and r.nearest_reachable_grid_value is None


def test_threshold_exactly_on_grid_is_reachable(toy_table, toy_config):
    table = canonicalize(toy_table, toy_config)
    row = table.row("T_0004")  # X:50+Y:50 at NCO 1.8, k = 30
    exact = row["mdi_fraction"]
    sol = solve_backward_threshold(table, "T_0004", threshold=float(exact))
    r = check_reachability(table, sol)
    assert r.reachable and abs(r.nearest_reachable_grid_value - 1.8) < 1e-9
