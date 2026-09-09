# Latest Database Sync — 2026-09-09

This note reconciles `PUR-Essay` with the latest scientific outputs committed in `stloendays/Database-For-PUR` at commit `d1f6d818702e56769564be1759fa4d6fc83abc52`.

## 1. Scientific definition changed

The earlier FRONTIER/ORACLE objective used three terms: eta80, eta120 and eta80/eta120. Those are not three independent rheological degrees of freedom because the ratio is algebraically determined by eta80 and eta120.

The latest database-derived decision state therefore uses two independent coordinates:

```text
eta120 + thermal sensitivity (eta80/eta120)
```

with eta80 retained as a hard processing-window gate.

The database summary defines

```text
J_state = (log10(eta120/eta120*) / h_eta120)^2
        + (log10(ratio/ratio*) / h_ratio)^2
```

with

```text
eta120* = 0.4242640687119285 Pa s
ratio*  = 8.154753215150045
h_eta120 = 0.1505149978319906 log10 units
h_ratio  = 0.06631278263729548 log10 units
```

This avoids triple-counting the same two-point temperature response.

## 2. Updated deterministic decision state

According to `data/derived/rheology_v2/decision_state_objective_summary.json` in the database repository:

- candidate space: 928 synthetic PUR_SIM_V1 states;
- property-state optimum: `WO_INV_0419`;
- blend: 50/50 PPG700/PPG1000;
- NCO:OH = 1.7;
- MDI fraction = 0.3406249, below the 0.35 floor;
- constrained optimum under the updated independent-state objective: `WO_INV_0420`;
- NCO:OH = 1.8;
- MDI fraction = 0.3535771;
- constrained J_state = 0.0296053;
- `WO_INV_0579` becomes the second-best feasible state under this updated objective, J_state = 0.0482197.

`WO_INV_0579` remains the frozen historical PUR-ORACLE V2 winner under the old three-term objective and must not be rewritten retroactively.

## 3. Backward design remains exactly interpretable

For the 50/50 PPG700/PPG1000 trajectory, the MDI-fraction lower bound is the active formulation boundary.

The exact continuous threshold is

```text
NCO:OH = 1.771983672436162
```

and the first reachable state on the 0.1 grid is

```text
NCO:OH = 1.8 -> WO_INV_0420
```

Thus the updated forward optimum and the backward-reachable formulation now meet at the same deployable candidate.

## 4. Robustness result is an empty-set result

The latest strict robustness audit uses the actual lower/upper response intervals, including the compounded interval of eta80/eta120. It does not replace those intervals with one common symmetric radius.

Result:

- nominal-feasible candidates: 117;
- strict robust-feasible candidates: 0;
- strict robust target reachable: false.

Therefore no L2 robust winner should be assigned under this strict definition.

The correct result is a reachability gap:

- nearest by preferred-window relaxation: `WO_INV_0359`;
- required preferred half-width expansion: 1.485626x (+48.56%);
- nearest by uniform uncertainty shrink: `WO_INV_0374`;
- minimum uncertainty reduction: 34.40%;
- `WO_INV_0420` itself would require 41.27% uncertainty reduction;
- its limiting coordinate is the viscosity-ratio / thermal-sensitivity interval.

These are algorithmic statements about PUR_SIM_V1, not measurements of physical experimental uncertainty.

## 5. Consequence for the Agent benchmark

The Agent task must now recover a decision chain of the form

```text
property optimum
  -> nominal constrained optimum
  -> robust-set emptiness / reachability gap
  -> active MDI boundary
  -> backward threshold
  -> discrete reachable state
```

A model that invents an L2 winner when the strict robust set is empty is scientifically wrong even if it names a plausible candidate.

The primary benchmark should therefore score correct no-winner recovery for the robust layer, not force a candidate ID.

## 6. Remaining blocker in PUR-Essay

The latest database repository contains the derived decision and robustness summaries, but the exact row-level PUR_SIM_V1 response table required for a self-contained blinded recomputation is still not committed to `PUR-Essay`.

Do not reconstruct the missing 928 response rows from summary values, the old v0.7 predictor, or a common uncertainty radius.

Before freezing a new blind gold bundle, restore the exact row-level response table and the actual lower/upper interval columns used by the strict robustness audit. Until then:

- the latest database-derived scientific conclusions can be documented and used to redesign the benchmark;
- historical ORACLE V2 remains frozen provenance;
- a new fully self-contained RECOVER gold should not be declared reproducible from `PUR-Essay` alone.
