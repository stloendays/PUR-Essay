# Manuscript workspace

This directory contains the versioned manuscript source for PUR-Essay.

## Active manuscript state

Title: **From Temperature-Amplified Rheology to Auditable Formulation Decisions in Polyurethane Prepolymers**

- v0.2: source-grounded rheology + pre-FRONTIER draft.
- v0.3: first fully frozen PUR-FRONTIER V1 decision manuscript.
- `NON_AGENT_RESULTS_V2.md`: **authoritative replacement text for the non-Agent Results core**; this will be merged into manuscript v0.4 before the formal Agent benchmark is reported.

The old v0.3 passages that describe Pugar-derived 80/120 °C comparisons are superseded. The current source-grounded analysis uses 45/75 °C values inside the experimental source range; 120 °C extrapolations are not reported as experimental measurements.

## Deterministic paper core now available

### Source-grounded rheology

- 39 prepolymers / 4,559 usable temperature–viscosity points.
- Andrade median R² = 0.9967; 37/39 at R² >= 0.98.
- apparent activation energy spans 34.74–94.15 kJ mol⁻¹.
- matched free-NCO families: median viscosity multiplier per +1 wt%-point NCO ≈ 0.709 at 45 °C and 0.736 at 75 °C; median dEa/dNCO ≈ −0.81 kJ mol⁻¹ per wt%-point.
- matched C/P chemistry contrast: median ≈ 8.85 at 45 °C and 4.63 at 75 °C; low-temperature amplification ≈ 1.91×.
- direct patent temperature-induced rank reversal: US5932680A Example 1 vs Example 4 changes from 190 > 98 Pa·s at 90 °C to 55 < 60 Pa·s at 110 °C.
- patent composition-context interaction: 1.654× versus 1.091×; ratio-of-ratios = 1.516.

### Frozen PUR-FRONTIER V1

```text
928 total candidates
141 nominally feasible
117 robust-admissible

L0 property winner      WO_INV_0419
L1 constrained winner   WO_INV_0579
L2 robust winner        WO_INV_0420
```

The complete PUR_SIM_V1 response table is reconstructed from the historical multipart XZ/base64 snapshot and SHA256-verified before analysis.

Rank propagation over the 117 robust-admissible candidates:

```text
Spearman rho = 0.9851
Kendall tau  = 0.8918
367 / 6786 inversions = 5.41%
Top-1: WO_INV_0579 -> WO_INV_0420
```

Fixed 50/50 PPG700/PPG1000 NCO control:

```text
Kendall tau = 1.0
0 / 28 inversions
```

Backward design from `WO_INV_0419` gives the MDI-fraction boundary at NCO:OH = 1.77198 and the first reachable grid point at 1.8 (`WO_INV_0420`).

### FRONTIER-DEPTH V1

The frozen decision is now accompanied by decision-stability analysis rather than reported as an isolated winner:

- **constraint phase map:** varying the MDI lower bound creates discrete nominal and robust winner regimes;
- **uncertainty crossover:** `WO_INV_0579 -> WO_INV_0420` at uncertainty scale `s ≈ 0.3637`;
- **robustness cliff:** no broad-window robust state remains above `s ≈ 1.8063`;
- **terminal bottleneck:** viscosity ratio / thermal sensitivity;
- **objective-weight stability:** 50,000 sampled weight vectors; nominal basin led by 0579 (~79.8%), robust basin led by 0420 (~44.2%) and 0341 (~36.3%);
- **Pareto opportunity set:** 44/117 robust-admissible candidates are non-dominated under the five-objective audit;
- **objective geometry:** eta80, eta120 and eta80/eta120 contain only two independent response degrees of freedom; the frozen three-term objective induces a 3:1 principal metric anisotropy. An independent two-DOF state materially reorders the robust frontier and yields alternative-state L2 = `WO_INV_0404`;
- **prospective model-structure hypothesis:** real rheological stoichiometric sensitivity is likely chemistry-dependent, whereas PUR_SIM_V1 intentionally uses an almost blend-invariant NCO:OH sensitivity.

## Figure status

- **Figure 2** — final R/PNG/PDF/SVG; 45–75 °C source-range Andrade response.
- **Figure 3** — final R/PNG/PDF/SVG; free-NCO coupling at 45/75 °C.
- **Figure 4** — final R/PNG/PDF/SVG; chemistry amplification + patent context interaction + direct rank reversal.
- **Figure 5** — final R/PNG/PDF/SVG; MDI constraint phase map + nominal-to-robust rank inversion.
- **Figure 6** — final R/PNG/PDF/SVG; uncertainty phase map + robustness cliff + objective-geometry sensitivity.
- **Figure 7** — reserved for formal repeated PUR-RECOVER API benchmark.
- **Figure 8** — reserved for prospective wet-lab validation.

Figures 5–6 are not schematics. Their R workflow reconstructs the frozen 928-row response snapshot, recomputes PUR-FRONTIER V1 and FRONTIER-DEPTH V1, verifies the gold state, and only then renders publication outputs.

## Intentionally pending

1. **PUR-RECOVER V1 formal API benchmark:** repeated real-model trials, baselines and ablations on the frozen anonymized bundle.
2. **Figure 7:** render only after the repeated Agent benchmark is complete.
3. **Prospective wet-lab validation:** test target-window transfer and the stronger chemistry × stoichiometry interaction hypothesis.
4. **Manuscript v0.4:** merge `NON_AGENT_RESULTS_V2.md` into the full article, update Abstract/Methods/Discussion and renumber the Agent/experiment sections.
5. Authors, affiliations, acknowledgements, journal formatting and final reference pass.

Mock Agent runs are infrastructure tests and must not be reported as model performance.

## Claim boundary

- Experimental/public rheology evidence supports the physical conclusions in the source-grounded rheology sections.
- `PUR_SIM_V1` is a synthetic finite-space decision benchmark; it supports deterministic ranking propagation, decision-phase analysis, robustness, backward design and Agent evaluation only.
- The objective-geometry alternative is a sensitivity analysis and does not overwrite the frozen FRONTIER V1 gold rule.
- Historical PUR-ORACLE V2 remains frozen for provenance.
- Agent performance and prospective wet-lab results remain independent of the deterministic answer definition.

## Reproduction

```bash
python scripts/freeze_frontier_v1.py
python scripts/analyze_frontier_depth_v1.py
Rscript figures/R/render_all_figures.R
```

GitHub Actions executes the same pipeline and stores PNG/PDF/SVG outputs plus the frozen deterministic analysis artifacts.
