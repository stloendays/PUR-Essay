# Manuscript workspace

This directory contains the versioned manuscript source for PUR-Essay.

## Active draft

- `PUR_manuscript_draft_v0.2.md`
- Title: **From Temperature-Amplified Rheology to Auditable Formulation Decisions in Polyurethane Prepolymers**
- Status: scientific draft; source-grounded rheology results are written, while final FRONTIER, Agent and experimental results remain explicitly pending.

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
- Methods, Discussion, Conclusions and preliminary references.
- Figure 2-4 captions aligned to the formal R sources in `figures/R/` and rendered outputs in `figures/final/`.

## FRONTIER V1 status

The pre-freeze robustness definition has now been audited and fixed **before** any FRONTIER gold is generated.

Current rule:

1. L0: nominal property score over all 928 candidates.
2. L1: nominal point-response rheology + chemistry/process constraints. Uncertainty intervals are not a nominal hard gate.
3. L2: parameter-free minimax worst-case extension of the same log-space objective over the frozen uncertainty interval, with `domain_ratio <= 1.0` as the additional robust eligibility condition.
4. Full-interval containment inside broad/preferred windows is diagnostic only and is not used to delete candidates.
5. No L2 winner is hard-coded. The earlier `WO_INV_0420` result remains a prior hypothesis and a verified first-reachable point on the 50/50 backward trajectory, not the final robust gold.

Definition: `configs/frontier_v1.json`. Rationale: `docs/FRONTIER_V1.md`.

The exact L0/L1/L2 frontier still cannot be frozen because the original complete `PUR_SIM_V1` 928-row response table is absent from the repository. The old v0.7 model output is not a valid replacement and no missing responses are fabricated.

## Intentionally pending

1. **Restore the exact PUR_SIM_V1 response table** as `data/pur_sim_v1/candidates_full.csv` and run `scripts/freeze_frontier_v1.py`.
2. **Figure 5**: render the final decision-frontier propagation only after the full-table freeze. A schematic must not be substituted for data-derived L0/L2 results.
3. **PUR-RECOVER V1 benchmark**: build the blind bundle from frozen FRONTIER gold and run repeated API experiments.
4. **Figure 6**: render Agent benchmark after repeated runs are complete.
5. **Prospective wet-lab results**: insert only after the frozen experimental matrix is completed; never expose these results to the primary blind Agent bundle.
6. Authors, affiliations, acknowledgements, journal-specific formatting and final reference pass.

## Already verified independently of the missing response table

For the 50/50 PPG700/PPG1000 design trajectory:

- `mdi_parts = 30.3875 * NCO:OH`;
- the 35 wt% MDI boundary occurs continuously at NCO:OH = 1.7720;
- the first reachable frozen grid point is NCO:OH = 1.8 (`WO_INV_0420`);
- NCO:OH = 1.7 (`WO_INV_0419`) lies below the MDI floor at approximately 34.06 wt%.

These are backward/reachability results from the real design grid, not assertions about the final L0 or L2 winner.

## Claim boundary

- Experimental/public rheology evidence supports the physical conclusions in Sections 2.1-2.5.
- Synthetic `PUR_SIM_V1` responses support finite-space decision/benchmark analyses only and are not empirical rheology evidence.
- Historical `PUR-ORACLE V2` remains frozen for provenance and is not silently rewritten.
- FRONTIER V1 has a fixed pre-result decision rule, but no new L0/L2 gold is reported until the exact full response table is restored.
- Prospective wet-lab data and evaluator-only gold files remain outside the primary blinded Agent input.

## Figure sources

- `figures/R/Figure2.R` -> `figures/final/Figure2_temperature_Andrade.*`
- `figures/R/Figure3.R` -> `figures/final/Figure3_free_NCO_coupling.*`
- `figures/R/Figure4.R` -> `figures/final/Figure4_chemistry_amplification_interaction.*`
- Figure 5 -> pending frozen full-table FRONTIER results.
- Figure 6 -> pending repeated PUR-RECOVER results.

All future manuscript revisions should create a new versioned draft or update the active draft with an explicit commit message. Do not alter frozen historical files or scientific definitions post hoc to make later results look cleaner.
