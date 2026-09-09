# Manuscript workspace

This directory contains the versioned manuscript source for PUR-Essay.

## Active draft

- `PUR_manuscript_draft_v0.2.md`
- Title: **From Temperature-Amplified Rheology to Auditable Formulation Decisions in Polyurethane Prepolymers**
- Status: scientific draft; source-grounded rheology results are written, while frontier/Agent/experimental results remain explicitly prospective.

## Completed in v0.2

- Abstract and Introduction.
- Source/protocol heterogeneity section.
- Andrade rheology analysis for 39 prepolymers / 4,559 temperature-viscosity points.
- Free-NCO coupling analysis.
- Temperature-amplified chemistry contrast.
- US5932680A composition-context interaction.
- Historical PUR-ORACLE V2 constrained-decision section.
- Backward-design interpretation.
- PUR-RECOVER V1 methodology and complete-decision-recovery definition.
- Prospective wet-lab validation design.
- Methods, Discussion, Conclusions, preliminary references.
- Figure 2-4 manuscript captions aligned to the formal R sources in `figures/R/` and rendered outputs in `figures/final/`.

## Intentionally pending

1. **PUR-FRONTIER V1**: freeze a scientifically justified robust-ranking definition before reporting a robust winner.
2. **Figure 5**: render decision-frontier propagation after PUR-FRONTIER V1 is frozen.
3. **PUR-RECOVER V1 benchmark**: run repeated blinded API experiments and insert complete-decision-recovery results.
4. **Figure 6**: render Agent benchmark after repeated runs are complete.
5. **Prospective wet-lab results**: insert only after the frozen experimental matrix has been completed; do not use these results in the primary blind Agent bundle.
6. Authors, affiliations, acknowledgements, journal-specific formatting and final reference pass.

## Claim boundary

- Experimental/public rheology evidence supports the physical conclusions in Sections 2.1-2.5.
- Synthetic `PUR_SIM_V1` responses support finite-space decision/benchmark analyses only and are not empirical rheology evidence.
- Historical `PUR-ORACLE V2` remains frozen for provenance and should not be silently rewritten.
- The robust decision layer is not yet frozen; the Agent must abstain rather than invent a robustness weighting.
- Prospective wet-lab data and evaluator-only gold files must remain outside the primary blinded Agent input.

## Figure sources

- `figures/R/Figure2.R` -> `figures/final/Figure2_temperature_Andrade.*`
- `figures/R/Figure3.R` -> `figures/final/Figure3_free_NCO_coupling.*`
- `figures/R/Figure4.R` -> `figures/final/Figure4_chemistry_amplification_interaction.*`

All future manuscript revisions should create a new versioned draft or update the active draft with an explicit commit message. Do not overwrite frozen scientific benchmark definitions to make later results look cleaner.
