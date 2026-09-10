# Prospective wet-lab validation V3 — local rheology and decision-point validation

**Status:** current wet-lab plan. This document corresponds to the laboratory execution plan `HMPUR 局部流变与最优点验证实验执行单 v5`.

**Supersedes for current execution:** `docs/VALIDATION_EXPERIMENT_V2.md`, which is retained only as historical provenance for the earlier single-point `WO_INV_0579` validation concept.

## Purpose

The wet-lab experiment is a **prospective validation layer**, not a formulation-screening stage and not an input to PUR-RECOVER V1.

The current experiment is designed to test four pre-declared questions:

1. Does the frozen robust decision point fall in the intended processing-rheology window in real material?
2. At fixed PPG700/PPG1000 composition, does increasing NCO:OH lower melt viscosity across temperature?
3. At fixed NCO:OH, does changing PPG700/PPG1000 composition change viscosity level and thermal sensitivity?
4. Does MDI reaction amplify or reshape composition-dependent rheological differences when comparing the paired pre-MDI blend and post-reaction prepolymer?

The experiment does **not** choose a new winner after seeing measurements. The computational candidate definitions remain frozen.

## Full publication-priority matrix

Use five formulations centred on the current robust decision point. Each formulation is synthesized in **three independent batches**.

| Role | Candidate | PPG700 / PPG1000 | NCO:OH | Nominal MDI parts / 100 polyol | Nominal MDI mass fraction | Scientific role |
|---|---|---:|---:|---:|---:|---|
| `N-` | `WO_INV_0419` | 50 / 50 | 1.70 | 51.6588 | 34.06% | lower-stoichiometry boundary control; property-near-optimal but below the 35% MDI floor |
| `OPT` | `WO_INV_0420` | 50 / 50 | 1.80 | 54.6975 | 35.36% | current robust/final decision point |
| `N+` | `WO_INV_0421` | 50 / 50 | 1.90 | 57.7363 | 36.60% | higher-stoichiometry neighbour |
| `C-` | `WO_INV_0404` | 60 / 40 | 1.80 | 56.6280 | 36.15% | PPG700-rich feasible composition neighbour |
| `C+` | `WO_INV_0436` | 40 / 60 | 1.80 | 52.7670 | 34.54% | PPG1000-rich boundary control; nominally attractive rheology but below the 35% MDI floor |

Full design:

```text
5 formulations x 3 independent synthesis batches = 15 independent syntheses
```

A resource-limited minimum is the stoichiometry axis only (`N- / OPT / N+`) with three independent batches each (9 syntheses), but that reduced design cannot test the composition axis or pre/post reaction amplification with the same strength.

## Pre-MDI / post-MDI paired sampling

For every independent synthesis batch:

1. Prepare the intended PPG700/PPG1000 blend with an **extra 12.00 g** of the same blend beyond the reaction charge.
2. Dry the combined blend under the defined dehydration conditions.
3. Under dry nitrogen, remove **12.00 g** as the paired **pre-MDI polyol-blend sample** and seal it immediately.
4. Add MDI to the remaining polyol charge using the actual remaining polyol mass.
5. If the actual removed pre-MDI sample differs from 12.00 g by more than 0.10 g, recalculate the MDI charge from the actual remaining polyol mass before addition.

This gives a within-batch comparison between:

```text
pre-MDI polyol blend  ->  post-reaction NCO-terminated prepolymer
```

and allows the paper to distinguish a pre-existing blend-composition effect from a reaction-induced amplification/reshaping effect.

## Raw materials and stoichiometric correction

The conceptual design uses PPG700 and PPG1000. The laboratory material must record the exact commercial grade and lot.

Recommended interpretation:

- commercial PPG ~725 is a materialization of conceptual PPG700, not an exact identity;
- PPG ~1000 is treated analogously;
- actual hydroxyl numbers from the lot COA/assay must be used for stoichiometric correction;
- actual MDI NCO content must be used where available; nominal purity is not a substitute for measured/assayed NCO wt%; if necessary, determine NCO content by the laboratory's validated isocyanate assay.

The correction is used to preserve the pre-declared **NCO:OH**, not to tune the formulation after viscosity results become known.

## Nominal 300 g charge examples

The following are illustrative calculations using OH700 = 147 mg KOH/g, OH1000 = 111 mg KOH/g and MDI NCO = 33.6 wt%. Formal batch sheets must use the actual lot values.

| Role | PPG700 (g) | PPG1000 (g) | MDI (g) | Final nominal mass (g) |
|---|---:|---:|---:|---:|
| `N-` | 100.75 | 100.75 | 98.50 | 300.00 |
| `OPT` | 98.84 | 98.84 | 102.32 | 300.00 |
| `N+` | 97.00 | 97.00 | 106.00 | 300.00 |
| `C-` | 117.49 | 78.33 | 104.19 | 300.01 |
| `C+` | 79.83 | 119.75 | 100.42 | 300.00 |

The extra 12.00 g pre-MDI sampling blend is added proportionally before drying and is not included in the 300 g final-product basis above.

## Synthesis procedure

1. Charge the required PPG700/PPG1000 blend plus the extra pre-MDI sampling quantity.
2. Dehydrate at approximately **70 °C under vacuum**; target residual water <= 0.05 wt% where the laboratory can verify it.
3. After dehydration, take the paired 12.00 g pre-MDI sample under dry nitrogen and seal.
4. Bring the remaining blend to the defined addition condition; add the calculated amount of 4,4'-MDI using consistent addition and mixing practice across all batches.
5. React under dry nitrogen at approximately **110 °C**. Use ~3 h as a process reference, but endpoint is governed by NCO stability rather than an arbitrary clock time.
6. From ~2 h onward, take NCO samples every 30-60 min where practical. Two consecutive measurements with absolute difference <= 0.20 wt% indicate near-stability; if not stable at 3 h, continue and record the actual reaction time.
7. Do not add extra raw material after observing viscosity/NCO in order to force agreement with the prediction.

## NCO endpoint

The theoretical residual NCO must be calculated for each formulation from the actual hydroxyl values and MDI NCO content.

Illustrative nominal residual NCO values at MDI NCO = 33.6 wt% are:

```text
N-   ~4.71 wt%
OPT  ~5.28 wt%
N+   ~5.83 wt%
C-   ~5.40 wt%
C+   ~5.16 wt%
```

Suggested agreement interpretation:

```text
|NCO_measured - NCO_theory| <= 0.20 wt%   ideal
|NCO_measured - NCO_theory| <= 0.30 wt%   acceptable with documentation
```

These are synthesis-QC criteria, not a rule for post-hoc reformulation.

## Rheology measurement plan

Measure both the pre-MDI blend and post-reaction prepolymer at:

```text
80, 90, 100, 110 and 120 °C
```

For each `formulation x batch x stage x temperature`:

- use separate aliquots rather than repeatedly heating and reusing the same sample;
- pre-equilibrate for approximately 60 min under the defined protocol;
- target temperature control within approximately +/-0.5 °C;
- start with two technical measurements;
- if the relative difference is >5%, perform a third technical measurement;
- if three technical values still have CV >10%, flag an instrument/sample-handling anomaly rather than silently averaging it away.

Use the same rheometer geometry and shear condition across comparable samples whenever the torque range allows. The historical hot-melt protocol used a cone-plate geometry and fixed rotational condition; if a different geometry or shear rate is required to remain inside the instrument range, record it explicitly and do not compare unmatched conditions as though they were identical.

The independent synthesis batch is the biological/material statistical unit. Technical repeats quantify measurement repeatability and do not replace independent synthesis replication.

For the full design, the planned minimum number of viscosity readings is approximately:

```text
5 formulations x 3 batches x 2 stages x 5 temperatures x 2 technical replicates
= 300 viscosity readings
```

with additional third measurements where the duplicate discrepancy rule is triggered.

## Andrade-state analysis

For each `formulation x batch x stage`, fit:

```text
ln(eta) = A + B/T
Ea,app = R * B
```

where `T` is absolute temperature.

Fit-quality interpretation:

```text
R2 >= 0.98      preferred/clean fit
0.95 <= R2 < .98 retain but inspect temperature history and measurement range
R2 < 0.95       investigate before mechanistic interpretation
```

Compare both viscosity level and apparent activation energy rather than reducing the entire temperature response to a single viscosity number.

## Frozen PUR_SIM_V1 reference curves

The following values are **synthetic preregistered reference predictions**, not wet-lab observations and not acceptance targets for intermediate temperatures.

| Role | eta80 | eta90 | eta100 | eta110 | eta120 | Ea,app (kJ/mol) |
|---|---:|---:|---:|---:|---:|---:|
| `N-` | 3.426 | 1.941 | 1.134 | 0.681 | 0.420 | 60.58 |
| `OPT` | 3.338 | 1.884 | 1.097 | 0.657 | 0.404 | 60.98 |
| `N+` | 3.251 | 1.829 | 1.061 | 0.633 | 0.388 | 61.38 |
| `C-` | 3.176 | 1.799 | 1.051 | 0.631 | 0.389 | 60.60 |
| `C+` | 3.509 | 1.974 | 1.145 | 0.684 | 0.419 | 61.34 |

For the frozen computational model, the pre-declared qualitative directions are:

- along the 50/50 composition axis, increasing NCO:OH from 1.7 -> 1.9 lowers predicted viscosity across the temperature range;
- at NCO:OH = 1.8, increasing the PPG1000 fraction from 40% -> 60% raises predicted viscosity across the temperature range.

The direction of the experimentally fitted `Ea,app` response is **not** a pass/fail criterion. It is an empirical science result to be measured because public matched-family data suggest chemistry-dependent stoichiometric sensitivity and do not justify assuming the synthetic benchmark's Ea trend is physically universal.

## Primary validation windows for the OPT decision point

For `WO_INV_0420`, preserve the frozen preferred processing windows as the primary transfer check:

```text
eta80       2.2 - 5.5 Pa.s
eta120      0.30 - 0.60 Pa.s
eta80/eta120 7.0 - 9.5
```

The intermediate 90/100/110 °C points are used to estimate curve shape and `Ea,app`; do not invent post-hoc acceptance windows for them after seeing the data.

A successful physical transfer does not require matching every synthetic prediction to the third decimal place. The stronger criterion is that the real material reproduces the intended process window and the pre-declared local trend structure with acceptable independent-batch reproducibility.

## Statistical and reproducibility priorities

- Main unit: independent synthesis batch (`n = 3` per formulation in the full plan).
- Batch-level CV for key viscosity/Ea measures: <=5% is preferred; <=10% is generally acceptable with full reporting.
- Report all batches, including failed or outlying syntheses with documented process deviations.
- Do not delete a formulation because it weakens the computational story.
- Preserve raw rheometer exports, batch records, COAs/assays, NCO calculations and analysis scripts.

## Optional but recommended add-on experiments

These are not substitutes for the core five-formulation rheology matrix.

### 1. ATR-FTIR — recommended first add-on

Measure paired pre-MDI and final prepolymer samples for at least `OPT` and representative controls. Use it as qualitative/semquantitative chemical evidence of urethane formation and residual isocyanate functionality. FTIR does not replace the NCO assay.

### 2. Shear-rate sweep — recommended second add-on

At minimum on `OPT` plus representative stoichiometry/composition controls, perform shear-rate sweeps at selected temperatures (preferably including 80 and 120 °C). This checks whether the apparent formulation ranking depends materially on the chosen shear condition.

### 3. SEC/GPC — useful mechanistic add-on if available

Use molecular-weight distribution to help interpret whether viscosity differences track chain growth/distribution as stoichiometry and polyol composition change. This is useful but lower priority than the core rheology, NCO QC, FTIR and shear-condition control.

### 4. Adhesion demonstration — optional application layer

Peel/adhesion can be added as a small application demonstration if resources permit, but it is not required to establish the current rheology/decision-frontier manuscript claims and should not displace the core experiment.

## Separation from PUR-RECOVER V1

Wet-lab outcomes are never supplied to the primary blinded Agent benchmark. The ordering remains:

```text
deterministic science frozen
-> blind Agent benchmark frozen/run
-> prospective wet-lab validation opened and interpreted independently
```

Agent performance tests **decision recoverability**. Wet-lab experiments test **physical transferability**.

## Current manuscript role

This experiment is intended to become Figure 8 / the prospective physical-validation section after data collection. Until real measurements exist, no experimental result should be fabricated, backfilled from PUR_SIM_V1, or written as though already observed.
