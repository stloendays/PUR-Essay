# Manuscript workspace

This directory contains the versioned manuscript source for PUR-Essay.

## Active manuscript state

Working title: **From Temperature-Amplified Rheology to Auditable Formulation Decisions in Polyurethane Prepolymers**

The paper is now organized around an **Agent-guided, human-in-the-loop wet-lab validation** rather than treating experiment as a future appendix-style check.

- v0.2: source-grounded rheology + pre-FRONTIER draft.
- v0.3: first fully frozen PUR-FRONTIER V1 decision manuscript.
- `NON_AGENT_RESULTS_V2.md`: authoritative non-Agent computational/source-grounded Results replacement text.
- `EXPERIMENTAL_RESULTS_V1.md`: **authoritative wet-lab Results core for the next full manuscript revision.**
- `../docs/AGENT_EXPERIMENT_INTERFACE_V1.md`: current definition of the Agent recommendation / human actuation boundary.
- `../docs/VALIDATION_EXPERIMENT_V8_AGENT_GUIDED.md`: current interpretation of the executed experiment.

The old v0.3 passages that describe Pugar-derived 80/120 °C comparisons are superseded. The current source-grounded analysis uses 45/75 °C values inside the experimental source range; 120 °C extrapolations are not reported as experimental measurements.

## Revised paper hierarchy

The central workflow is now:

```text
1. source evidence + frozen formulation decision state
2. explicit chemistry and process-state representation
3. Agent quantifies uncertainty / robustness and recommends test points
4. recommendation is frozen
5. human operator executes the recommended wet-lab point
6. physical result adjudicates the Agent recommendation
7. process-state evidence returns to the next design iteration
8. PUR-RECOVER independently audits reproducibility of the decision chain
```

The experiment is the physical centre of the article, but the Agent is the **decision/recommendation bridge** between the computational state and the experiment. The Agent is not described as physically operating the laboratory.

## Process-state variables now entering the design flow

The next design representation explicitly separates

```text
x_chem = formulation variables
z_proc = {
  reaction_history,
  thermal_hold_time,
  preparation_perturbation
}
```

These process variables are scientifically known. The current study does not claim to discover their existence. Instead, the experiment quantifies how strongly they alter rheology in this system and turns them into structured variables/uncertainty dimensions for the next recommendation cycle.

This changes the interpretation of the original variability:

- E2 repeat dispersion is evidence of preparation/history sensitivity, not merely failed reproducibility;
- the 120 °C hold curves quantify thermal-hold sensitivity as an explicit process coordinate;
- the Agent's role is to account for this uncertainty when recommending robust or diagnostic points;
- the human experiment is what physically changes the state and produces the observation.

## Primary wet-lab result

### Original local design

- E1/E2/E3 vary NCO:OH = 1.70/1.80/1.90 at PPG2000/PDP-70 = 50/50.
- E4/E5 vary PPG2000/PDP-70 = 60/40 and 40/60 at NCO:OH = 1.80.
- Recorded 80-130 °C sweeps decrease monotonically with temperature.
- E2 repeated runs show large absolute-level dispersion: max/min ≈ 2.89× at 80 °C and 3.57× at 120 °C.
- At 120 °C, E1 rises by 9.51% over 15-60 min and 16.85% over 15-90 min.
- E5 rises by 51.54% over 15-60 min and 93.08% over 15-90 min.

### Agent-recommended follow-up / final physical adjudication

The supplied follow-up formulation uses PPG2000/PDP-70/AC1920/TK100/MDI = 39.60/39.60/17/5/20.19 on the source-reported parts basis.

Two repeat runs of this **same formulation** give 120 °C viscosity drifts of -0.16% and +3.04% from 15 to 60 min. Their mean profile changes by ~1.47%, and the pointwise two-run CV is ~2.87-5.11%.

The fair original-versus-follow-up comparison is the shared 15-60 min interval. No 90-min follow-up measurement is fabricated or implied.

Under the project chronology, the Agent recommendation preceded the final repeated measurement. The final manuscript must attach the corresponding immutable pre-result recommendation/run/commit. With that provenance, the final repeated experiment is described as **prospective physical adjudication of the Agent recommendation**.

The scientific wording is therefore:

> The Agent selected/recommended the experimental point under uncertainty; a human operator executed the chemistry and measurement; the final repeated experiment supported the recommendation within the measured 120 °C, 15-60 min domain.

Not:

> The Agent autonomously performed the laboratory experiment.

## Agent–experiment interface

The application loop is

```text
computational evidence
-> uncertainty / decision-sensitivity evaluation
-> Agent recommendation
-> frozen recommendation + falsification/acceptance criterion
-> human wet-lab actuation
-> physical measurement
-> supported / partially supported / falsified / out-of-domain
-> next design iteration
```

A generic augmented design objective is

```text
J_next =
    w_eta L_eta
  + w_T L_temperature
  + w_S L_stability
  + lambda_U U(x_chem, z_proc)
  + feasibility_penalties.
```

This is a paper-facing architecture. Exact numerical results continue to come from their frozen deterministic implementations.

## Two Agent roles must remain separate

### Experimental recommendation Agent

Purpose:

```text
uncertainty-aware recommendation
-> human wet-lab execution
-> prospective physical adjudication
```

This is the Agent application that the final experiment validates.

### PUR-RECOVER benchmark Agent

Purpose:

```text
blind bundle
-> recover frozen deterministic decision chain
-> challenge / cross-check
-> certify
-> explain
```

PUR-RECOVER remains an independent benchmark of decision recovery and auditability. The primary blind Agent does not receive `data/prospective_validation/`, and the wet-lab result does not define its gold answer.

This separation allows the paper to show both **practical recommendation value** and **decision-process reproducibility** without circular validation.

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

These computational analyses support the experimental recommendation story rather than replace the physical test.

## Revised figure priority

- **Figure 1** — human-in-the-loop architecture with a visible digital/physical boundary: process-state representation -> Agent uncertainty evaluation -> recommendation -> human execution -> physical adjudication.
- **Figure 2** — local wet-lab 80-130 °C viscosity response and E2 preparation/history sensitivity.
- **Figure 3** — 120 °C hold response and repeated follow-up formulation response.
- **Figure 4** — recommendation-to-validation summary: uncertainty/process state, Agent-selected point, measured SI and transition to the augmented design state.
- Existing source-grounded/computational figures are shifted later and renumbered during the full v0.4 assembly.
- Formal PUR-RECOVER Agent performance remains a later, independent figure and is rendered only from repeated real-model benchmark results.

## Data and interface files

Wet-lab:

- `../data/prospective_validation/experimental_formulations_v1.csv`
- `../data/prospective_validation/experimental_viscosity_v1.csv`
- `../data/prospective_validation/experimental_summary_v1.csv`

Agent/experiment boundary:

- `../docs/AGENT_EXPERIMENT_INTERFACE_V1.md`
- `../configs/agent_experiment_recommendation_v1.schema.json`
- `../docs/VALIDATION_EXPERIMENT_V8_AGENT_GUIDED.md`

## Claim boundary

- The wet-lab data directly support temperature dependence, process/history sensitivity, thermal-hold viscosity build-up, and suppression of that build-up in the final repeated formulation.
- The Agent-validation claim requires a pre-result recommendation record for the final measurement; this is a provenance requirement, not a change to the observed data.
- The explanation that the follow-up works by lowering the effective reactive fraction is a mechanistic interpretation consistent with the formulation change; it is not presented as direct kinetic proof.
- `PUR_SIM_V1` remains a synthetic finite-space decision benchmark and is not relabelled as experimental data.
- The primary PUR-RECOVER benchmark remains isolated from wet-lab results.

## Next manuscript integration task

Assemble manuscript v0.4 around the **Agent recommendation -> human execution -> physical validation** story. Reaction history, hold time, and preparation perturbation should be introduced as explicit process-state variables rather than described as unknown hidden variables. No additional wet-lab experiment is required by the current manuscript plan; the remaining work is to attach/freeze the pre-result Agent recommendation provenance, produce the revised figures, and integrate the text into the full manuscript.
