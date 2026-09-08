# PUR-Bridge v1.1

**A publication-oriented, auditable HMPUR decision framework that turns failed global inverse design into a prospective experiment-selection problem.**

## Paper logic

`source-aware evidence -> frozen global baseline -> external falsification -> abstention -> structured patent anchors -> Agent experiment selection -> prospective E6* wet-lab test -> model update`

The central design choice is deliberate: **E1–E5 are not repeated in the laboratory.** Their published 130 C viscosities are frozen historical anchors for a preregistered missing-cell problem. Wet-lab evidence begins at E6*, a previously unreported C-rich/high-A counterfactual.

## Preregistered E6* hypotheses

At 130 C:

- H_strong: `27 x (43/26) = 44.65 Pa.s`
- H_weak: `27 x (24/22) = 29.45 Pa.s`
- equal-prior geometric midpoint: `36.27 Pa.s`
- robust zones: `<=33` weak-consistent; `33-40` indeterminate; `>=40` strong-consistent

The continuous mechanism statistic is

`theta = [ln(E6*/E5) - delta_D] / [delta_balanced - delta_D]`

where theta=0 is D-rich-like and theta=1 is balanced-like.

## Why an Agent is included

The LLM does **not** generate numerical predictions or formulations. Deterministic tools enforce:

- material-equivalence hard gates;
- information-gain calculation;
- minimum independent-batch replication;
- uncertainty-aware replicate/advance decisions;
- explicit abstention.

The LLM may retrieve provenance and explain tool outputs, but it cannot override them.

## Repository layout

- `data/historical_anchor_truth.csv` - frozen patent anchors used by the preregistered local model.
- `data/prospective_candidates.csv` - E6* plus deferred E7-E9 transfer candidates.
- `data/e6_measurement_template.csv` - raw-data schema for prospective E6* experiments.
- `data/material_equivalence_template.csv` - auditable raw-material gate input.
- `src/pur_bridge/` - anchor model, information gain, Agent policy, material gate, batch analysis and Andrade fitting.
- `scripts/` - reproducible analysis entry points.
- `docs/PAPER_MODEL_V1.md` - publication architecture.
- `docs/REPRODUCIBILITY_AND_CLAIMS.md` - claim boundaries and preregistration discipline.
- `legacy/` - frozen v0.7 summary/manifest retained as baseline evidence.

## Installation and tests

```bash
python -m pip install -e '.[dev]'
pytest
python scripts/run_anchor_analysis.py
```

Analyze real E6* data after filling the template:

```bash
python scripts/analyze_e6_batches.py path/to/e6_measurements.csv
```

Evaluate material compatibility:

```bash
python scripts/evaluate_material_gate.py path/to/material_audit.csv
```

## Scientific discipline

- Do not refit v0.7 to make the external failures disappear.
- Do not synthesize E1–E5 simply to clean up the historical story.
- Do not describe patent point values as noise-free experimental truth; they are frozen historical anchors.
- Do not call E7–E9 validated before measurement.
- Do not allow an LLM to create numerical predictions or bypass hard gates.
- Treat abstention and request-for-replication as valid scientific actions.

## Current status

The computational/preregistration layer is ready. **Current material-gate state is `AUDIT_REQUIRED` until real supplier documentation/COAs are entered.** No prospective E6* result is stored in this repository. Files under `examples/` are synthetic demonstrations only and must not be cited as experimental evidence.
