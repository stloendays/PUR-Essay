# E6* prospective experiment - publication-grade minimum protocol

## Scientific role

E1-E5 are frozen historical anchors and are **not** synthesized again. E6* is the first new wet-lab evidence. It is designed as the previously unreported C-rich/high-A counterfactual to patent Example 9.

The primary endpoint is **prepolymer melt viscosity at 130 C**. Pre-MDI blend viscosity and 110/120 C measurements are secondary, low-cost mechanistic/QC measurements taken from the same E6* batches; they do not turn E1-E5 back into experiments.

## Before synthesis: material gate

Fill `data/material_equivalence_template.csv` using actual supplier documentation and COAs and run:

```bash
python scripts/evaluate_material_gate.py material_audit.csv
```

- `ANCHOR_COMPATIBLE`: proceed with the patent-anchored prospective counterfactual interpretation.
- `SURROGATE_ONLY`: proceed only as a modern specification-matched transfer test.
- `AUDIT_REQUIRED`: resolve critical raw-material evidence first.
- `INCOMPATIBLE`: abstain from the historical absolute-viscosity test.

## Nominal formula, parts by mass

A 29.2; B 5.9; C 10.5; D 1.2; PPG425 23.4; beta-pinene tackifier 5.9; MDI 23.9.

This preserves the reported Example 9 non-A/B amounts and changes the A/B allocation within the polyester block. Final MDI mass must be recalculated from actual polyester/PPG OH values and MDI NCO content to preserve the intended NCO:OH ratio.

## Replication

- Minimum: **3 independent E6* syntheses** prepared separately.
- Primary 130 C condition: >=3 technical viscosity readings per batch after identical equilibration.
- Recommended secondary temperatures: 110, 120 and 130 C, using the same instrument/geometry conditions where feasible.
- Report batch means and between-batch variability. Technical readings never replace independent synthesis replication.

## Frozen interpretation at 130 C

- <=33 Pa.s: weak-transfer-consistent
- 33-40 Pa.s: indeterminate
- >=40 Pa.s: strong-transfer-consistent

The publication decision is stricter than point classification: the Agent advances to transfer-candidate ranking only if there are at least 3 independent batches **and** the batch-level 95% CI remains clear of the relevant 33/40 Pa.s boundary. Otherwise it requests another E6* batch.

Always report the continuous context-transfer coefficient `theta` and log Bayes-factor sensitivity at `sigma_log = 0.05, 0.08, 0.10, 0.12, 0.15`.

## Essential QC

- raw COAs: polyester OH value, water, acid value; PPG OH value/water; MDI NCO content;
- actual charges and calculated actual NCO:OH;
- dehydration temperature/time/vacuum;
- MDI-addition temperature and reaction temperature/time trace;
- post-reaction NCO content (wt% NCO, not "free MDI");
- Brookfield spindle/speed, equilibration time, raw readings and measurement timestamps.

## Data capture and reproducible analysis

Enter raw reads into `data/e6_measurement_template.csv` (copy it; do not overwrite the template) and run:

```bash
python scripts/analyze_e6_batches.py path/to/e6_measurements.csv
```

The script writes batch means, technical CVs, batch-level 95% CI, theta, Bayes-factor sensitivity, Agent next action and per-batch Andrade fits when all three temperatures are available.

## Optional characterization

ATR-FTIR and DSC are useful secondary checks, but independent synthesis replication and viscosity/NCO QC have higher priority.
