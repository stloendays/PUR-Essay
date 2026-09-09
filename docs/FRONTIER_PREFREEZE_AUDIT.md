# PUR-FRONTIER V1 pre-freeze audit

Date: 2026-09-09

## Purpose

This audit records the decision-rule correction made **before** the complete PUR_SIM_V1 response table is restored and before any new FRONTIER L0/L2 gold is generated.

The correction is intentionally version-local. Historical PUR-ORACLE V2 files are retained unchanged for provenance.

## Issue found

An earlier draft of `configs/frontier_v1.json` mixed two different questions:

1. Is the complete-data candidate nominally acceptable?
2. Is its uncertainty interval sufficiently narrow to remain entirely inside the target window?

The draft answered both with hard gates, including:

- full interval inside broad windows at L1;
- full interval inside preferred windows at L2.

This conflated nominal formulation selection with uncertainty certification.

It also made the robust layer unnecessarily brittle. For a log10 interval radius `r`, even a candidate exactly at a preferred-window centre can fit wholly inside the preferred window only if `r` is no larger than the half-width of that window in log space.

For the three preferred windows:

- eta80: 2.2-5.5 Pa.s -> centred half-width about **0.199 log10 units**;
- eta120: 0.30-0.60 Pa.s -> about **0.151**;
- eta80/eta120: 7.0-9.5 -> about **0.066**.

Thus full containment in all preferred windows effectively becomes a narrow-uncertainty certification dominated by the ratio window.

## Corrected FRONTIER rule

### L0 — property-only

All 928 candidates are ranked using the unchanged nominal objective:

```text
J = sum_k w_k log10(y_k/c_k)^2
```

where `c_k` is the geometric centre of the preferred window.

### L1 — nominal constrained

A candidate must satisfy the complete-data point-response and chemistry/process gates:

- broad eta80, eta120 and ratio windows;
- preferred eta80, eta120 and ratio windows;
- NCO:OH range;
- MDI mass-fraction range;
- chemistry-in-domain flag.

Uncertainty-interval containment is **not** a nominal hard gate.

### L2 — minimax robust

Among L1 candidates with `domain_ratio <= 1.0`, rank by the exact deterministic worst case of the same squared-log objective over the frozen interval:

```text
J_robust = sum_k w_k (abs(log10(y_k/c_k)) + r)^2
```

No uncertainty weight is tuned. No posterior distribution is assumed. No candidate is forced to remain fully within the preferred window over its entire interval.

Interval containment may still be reported as a diagnostic/sensitivity descriptor, but it does not define candidate eligibility.

## Why this is preferable

The rule now preserves a clear hierarchy:

```text
complete-data response -> nominal feasibility -> uncertainty propagation -> robust decision
```

rather than

```text
complete-data response -> uncertainty certification -> another uncertainty certification -> ranking
```

It is also aligned with the paper's core logic: the deterministic complete-data workflow first defines the admissible formulation landscape; uncertainty then changes how candidates are ranked for robustness.

## No winner was selected during this correction

The complete 928-row response table is absent from the repository. Therefore this audit does **not** claim a new L0 or L2 winner.

Previously documented IDs are retained only as audit hypotheses:

- `WO_INV_0419`: prior L0 property-only hypothesis;
- `WO_INV_0579`: historical frozen PUR-ORACLE V2 constrained winner;
- `WO_INV_0420`: prior robust hypothesis and independently verified first reachable point on the 50/50 PPG700/PPG1000 backward trajectory.

`WO_INV_0420` is not hard-coded as the FRONTIER V1 robust gold.

## Verified result that does not require response restoration

From `data/pur_sim_v1/design_space_928.csv`, the 50/50 PPG700/PPG1000 trajectory obeys:

```text
mdi_parts = 30.3875 * NCO:OH
```

For an MDI fraction floor of 0.35 on a 100-part polyol basis:

```text
NCO:OH* = 1.7720
```

and the first reachable frozen grid point is 1.8 (`WO_INV_0420`).

## Freeze condition

The exact original response table must be restored as:

```text
data/pur_sim_v1/candidates_full.csv
```

Only then should:

```bash
python scripts/freeze_frontier_v1.py
```

be used to compute and hash the new FRONTIER result.

No older model output, guessed reconstruction or synthetic fill-in is an acceptable substitute.
