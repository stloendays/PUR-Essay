# Manuscript workspace

This directory contains the versioned manuscript source for PUR-Essay.

## Active manuscript state

Working title: **From Temperature-Amplified Rheology to Auditable Formulation Decisions in Polyurethane Prepolymers**

The paper is now being reorganized around the executed wet-lab study rather than treating experiment as a future appendix-style validation.

- v0.2: source-grounded rheology + pre-FRONTIER draft.
- v0.3: first fully frozen PUR-FRONTIER V1 decision manuscript.
- `NON_AGENT_RESULTS_V2.md`: authoritative non-Agent computational/source-grounded Results replacement text.
- `EXPERIMENTAL_RESULTS_V1.md`: **authoritative experiment-first wet-lab Results core for the next full manuscript revision.**

The old v0.3 passages that describe Pugar-derived 80/120 °C comparisons are superseded. The current source-grounded analysis uses 45/75 °C values inside the experimental source range; 120 °C extrapolations are not reported as experimental measurements.

## Revised paper hierarchy

The evidence is now ordered by scientific role rather than by when the code modules were built:

```text
1. prospective local wet-lab validation
2. experimentally observed stability/process-sensitivity failure
3. formulation correction
4. repeated wet-lab confirmation of corrected stability
5. public/source-grounded rheology as external scientific context
6. frozen inverse/backward-design benchmark and decision-frontier analysis
7. blinded PUR-RECOVER Agent benchmark as an audit of decision recovery
```

The experiment is therefore the physical centre of the article. The synthetic `PUR_SIM_V1` benchmark remains clearly labelled as synthetic and is used for deterministic decision analysis and Agent evaluation only.

## Primary wet-lab result now available

The supplied experiment contains the original PPG2000/PDP-70/4,4'-MDI local design and a failure-aware corrected formulation.

### Original design

- E1/E2/E3 vary NCO:OH = 1.70/1.80/1.90 at PPG2000/PDP-70 = 50/50.
- E4/E5 vary PPG2000/PDP-70 = 60/40 and 40/60 at NCO:OH = 1.80.
- Recorded 80-130 °C sweeps decrease monotonically with temperature.
- E2 repeated runs show large absolute-level dispersion: max/min ≈ 2.89× at 80 °C and 3.57× at 120 °C.
- At 120 °C, E1 rises by 9.51% over 15-60 min and 16.85% over 15-90 min.
- E5 rises by 51.54% over 15-60 min and 93.08% over 15-90 min.

### Corrected formulation

The supplied correction uses PPG2000/PDP-70/AC1920/TK100/MDI = 39.60/39.60/17/5/20.19 on the source-reported parts basis.

Two repeat runs of this **same corrected formulation** give 120 °C viscosity drifts of -0.16% and +3.04% from 15 to 60 min. Their mean profile changes by ~1.47%, and the pointwise two-run CV is ~2.87-5.11%.

The fair original-versus-corrected comparison is the shared 15-60 min interval. No 90-min corrected measurement is fabricated or implied.

## External-validation terminology

The initial E1-E5 study can be described as **prospective external wet-lab validation** of the frozen computational design only insofar as these laboratory values were withheld from model fitting/decision freezing before the experiment.

The formulation correction is different. Because it was selected after observing the experimental failure mode, it is a **closed-loop follow-up validation**, not a blind external validation. This distinction is preserved throughout the manuscript.

## Deterministic paper core retained

### Source-grounded rheology

- 39 prepolymers / 4,559 usable temperature-viscosity points.
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

The frozen decision remains accompanied by decision-stability analysis:

- constraint phase map with discrete nominal and robust winner regimes;
- uncertainty crossover `WO_INV_0579 -> WO_INV_0420` at uncertainty scale `s ≈ 0.3637`;
- robustness cliff above `s ≈ 1.8063`;
- viscosity ratio / thermal sensitivity as the terminal bottleneck;
- 50,000 objective-weight samples;
- 44/117 robust-admissible candidates non-dominated under the five-objective audit;
- objective-geometry sensitivity demonstrating that the three-term rheology objective contains two independent response degrees of freedom.

These computational analyses now support the experimental story rather than define the paper's only central result.

## Revised figure priority

- **Figure 1** — overall experimental-first closed-loop workflow.
- **Figure 2** — local wet-lab 80-130 °C viscosity response and repeat/run sensitivity.
- **Figure 3** — 120 °C hold-stability failure and repeated corrected-formulation response.
- **Figure 4** — experimental stability/repeatability summary and stability-aware objective update.
- Existing source-grounded/computational figures are shifted later in the article and renumbered during the full v0.4 assembly.
- Formal PUR-RECOVER Agent performance remains a later figure and is rendered only from repeated real-model benchmark results.

## Data files for the experiment-first revision

- `../data/prospective_validation/experimental_formulations_v1.csv`
- `../data/prospective_validation/experimental_viscosity_v1.csv`
- `../data/prospective_validation/experimental_summary_v1.csv`

## Claim boundary

- The wet-lab data directly support temperature dependence, run/process sensitivity, thermal-hold viscosity build-up, and suppression of that build-up after formulation correction.
- The explanation that the correction works by lowering the effective reactive fraction is a mechanistic interpretation consistent with the formulation change; it is not presented as direct kinetic proof.
- `PUR_SIM_V1` remains a synthetic finite-space decision benchmark and is not relabelled as experimental data.
- The primary blind Agent benchmark remains isolated from `data/prospective_validation/` to avoid experimental-answer leakage.

## Next manuscript integration task

Assemble manuscript v0.4 by placing `EXPERIMENTAL_RESULTS_V1.md` ahead of the source-grounded rheology and FRONTIER sections, then update Abstract/Introduction/Methods/Discussion to match the new hierarchy. No additional wet-lab experiment is required by the current manuscript plan; the focus is analysis, figure production, and writing from the existing repeated measurements.