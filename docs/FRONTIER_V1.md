# PUR-FRONTIER V1 — deterministic decision frontier

Frozen definition: `configs/frontier_v1.json`. Implementation: `src/pur_science/`. Output:
`results/frontier_v1/` (via `scripts/freeze_frontier_v1.py`). Builds on PUR-ORACLE V2 without modifying it.

## Question

Not "which candidate has the best predicted viscosity" but

```text
property optimum  !=  chemically feasible optimum  !=  robust decision optimum
```

and, for each frontier crossing, *why* the decision moves and *what minimum change* crosses the boundary.

## Layers

| Layer | Set | Score | Tie-break |
|---|---|---|---|
| L0 property-only | all 928 | `J = Σ_k w_k log10(y_k / c_k)^2`, `c_k` = geometric centre of the preferred window (ORACLE V2 objective) | broad margin ↓, domain ratio ↑, ID |
| L1 nominal constrained | ORACLE V2 gates: broad + preferred windows, NCO:OH 1.3–3.0, MDI 35–49 wt% of polyol+MDI, chemistry in domain, full log10 interval inside broad window | `J` | same |
| L2 robust | L1 ∩ {whole log10 interval inside preferred windows} ∩ {domain ratio ≤ 1.0} | `J_robust = Σ_k w_k (|log10(y_k / c_k)| + r)^2`, `r` = frozen log10 interval radius | same |

`J_robust` is the worst case of `J` over the candidate's uncertainty interval. It is an interval statement, not a
distributional one; no p-values or posterior weights are introduced.

## Active constraint

The first failing nominal gate of the L0 winner in the priority order `mdi_fraction, nco_oh, chemistry_in_domain,
interval_inside_broad, broad windows, preferred windows`. Threshold and candidate value are reported.

## Backward design

On the frozen grid every blend obeys `mdi_parts = k_blend × NCO:OH` exactly (verified for all 58 blends). With
polyol basis `B = 100` and MDI-fraction floor `f = 0.35`:

```text
n* = f · B / (k_blend · (1 − f))
```

For PPG700:50 + PPG1000:50, `k = 30.3875` → `n* = 1.7720`. The reachability step projects `n*` onto the discrete
NCO:OH grid of the same blend and returns the first grid point whose MDI fraction satisfies the floor: **1.8**
(`WO_INV_0420`). If no grid point satisfies it, `reachable = false`.

## Local trends (evaluated at the L2 winner, or L1 if L2 is not frozen)

- `nco_direction`: direction of eta80 as NCO:OH increases along the same blend.
- `composition_direction`: direction of eta80 as the parts of the *axis component* increase at fixed NCO:OH within
  the same two-component family. The axis component is the one whose parts raise `mdi_parts` (higher hydroxyl
  demand). This definition is data-derived and therefore identical in anonymised and named tables.

Directions are `increase | decrease | flat | mixed` from the full local sweep, not from a single difference.

## Reproduction status

- `J`, MDI fraction, broad margin and the L1 ordering reproduce the frozen ORACLE V2 snapshot to machine precision
  (`tests/test_objective.py`).
- Backward threshold and reachability are reproduced on the real 928-row design grid (`tests/test_backward.py`,
  `tests/test_reachability.py`).
- L0 and L2 winners require the complete `PUR_SIM_V1` response table, which is not in the repository. The freeze
  script compares its result with the documented expectation (`WO_INV_0419` / `WO_INV_0579` / `WO_INV_0420`,
  1.772 → 1.8) and reports every disagreement; it never edits data.

## Claim boundary

PUR_SIM_V1 is a synthetic benchmark space. FRONTIER V1 results are algorithmic: finite-space optimisation, constraint
handling, uncertainty propagation as intervals and backward calculation. They are not experimental findings.
