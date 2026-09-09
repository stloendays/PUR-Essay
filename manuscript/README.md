# Manuscript workspace

This directory contains the versioned manuscript source for PUR-Essay.

## Active manuscript state

Title: **From Temperature-Amplified Rheology to Auditable Formulation Decisions in Polyurethane Prepolymers**

- v0.2: source-grounded rheology + pre-FRONTIER draft.
- v0.3: adds the fully frozen PUR-FRONTIER V1 decision results and Figure 5 interpretation.

## Results now complete enough for the deterministic paper core

### Source-grounded rheology

- 39 prepolymers / 4,559 temperature-viscosity points.
- Andrade median R² = 0.9967; 37/39 at R² >= 0.98.
- formulation-specific apparent activation energy.
- free-NCO coupling to viscosity and temperature sensitivity.
- temperature-amplified chemistry contrast.
- US5932680A composition-context interaction.

### Frozen PUR-FRONTIER V1

```text
928 total candidates
141 nominally feasible
117 robust-admissible

L0 property winner      WO_INV_0419
L1 constrained winner   WO_INV_0579
L2 robust winner        WO_INV_0420
```

Rank propagation over the 117 robust-admissible candidates:

```text
Spearman rho = 0.9851
Kendall tau  = 0.8918
367 / 6786 inversions = 5.41%
```

Fixed 50/50 PPG700/PPG1000 NCO control:

```text
Kendall tau = 1.0
0 / 28 inversions
```

Backward design from `WO_INV_0419` gives the MDI-fraction boundary at NCO:OH = 1.77198 and the first reachable grid point at 1.8 (`WO_INV_0420`), independently matching the robust L2 winner.

## Figure status

- Figure 2 — final R/PNG/PDF/SVG.
- Figure 3 — final R/PNG/PDF/SVG.
- Figure 4 — final R/PNG/PDF/SVG.
- **Figure 5 — now real-data-driven and generated from frozen `results/frontier_v1/`; final R/PNG/PDF/SVG.**
- Figure 6 — reserved for formal repeated PUR-RECOVER API benchmark.

Figure 5 is not a schematic. Its R source refuses publication rendering unless the FRONTIER manifest has `gold_status = GOLD`.

## Intentionally pending

1. **PUR-RECOVER V1 formal API benchmark**: build the anonymised blind bundle from frozen FRONTIER gold and run repeated real-model trials/baselines.
2. **Figure 6**: render only after repeated Agent results are available.
3. **Prospective wet-lab validation**: insert actual pre-MDI/prepolymer temperature-viscosity curves and Ea only after experiments are completed.
4. Authors, affiliations, acknowledgements, journal-specific formatting and final literature/reference pass.

Mock Agent runs are infrastructure tests and must not be reported as model performance.

## Claim boundary

- Experimental/public rheology evidence supports the physical conclusions in Sections 2.1-2.5.
- `PUR_SIM_V1` is a synthetic finite-space decision benchmark; it supports L0/L1/L2 decision propagation, backward design and Agent evaluation only.
- Historical PUR-ORACLE V2 remains frozen for provenance.
- PUR-FRONTIER V1 is now frozen and hash-reproducible.
- Prospective wet-lab data and evaluator-only gold remain outside the primary blind Agent input.

## Reproduction

```bash
python scripts/freeze_frontier_v1.py
Rscript figures/R/render_all_figures.R
```

The response table is reconstructed from the frozen multipart XZ/base64 snapshot and SHA256-verified before the frontier is produced.
