# PUR-Bridge v1.1 - publication model and manuscript architecture

## One-sentence claim

Under sparse, heterogeneous HMPUR evidence, reliable inverse design should not be judged only by whether it proposes a formulation; it should **arbitrate between global prediction and stronger local evidence, abstain when transfer is unsupported, and spend prospective experimental budget on the measurement with the highest decision value.**

## Why the paper is not a conventional ML paper

The frozen v0.7 results are retained as a falsification baseline. The global model recovers useful structure in some regimes but fails under chemistry/temperature shift, and its rigorous uncertainty gate returns 0 certified recommendations among 928 enumerated WO candidates. v1.1 does not refit those failures away.

Instead, the paper asks a different question: when a global predictor becomes unreliable, can structured historical evidence identify a scientifically sharper local decision problem, and can an auditable Agent choose the minimum new wet-lab evidence needed to resolve it?

## Evidence hierarchy

1. **Source-aware global evidence** - public papers/patents/datasets and the frozen v0.7 baseline provide broad context, external falsification and domain-risk information.
2. **Structured local anchors** - US5932680A Examples 5-9 are frozen historical anchor values. They are not remeasured and are not assigned artificial replicate precision.
3. **Missing-cell hypothesis layer** - two explicit transfer hypotheses predict the unreported C-rich/high-A counterfactual E6*.
4. **Material-equivalence gate** - actual E6* raw materials must be audited before historical absolute-viscosity interpretation is allowed.
5. **Agent decision layer** - deterministic tools own information gain, material gates, replication requirements and abstention; an LLM may retrieve provenance and explain the decision only.
6. **Prospective wet-lab layer** - new evidence begins at E6*, followed only by a later transfer experiment if the post-E6 decision state supports it.

## Frozen local model at 130 C

Historical anchors:

- E1 = 26 Pa.s; E2 = 43 Pa.s (balanced C/D)
- E3 = 22 Pa.s; E4 = 24 Pa.s (D-rich)
- E5 = 27 Pa.s (C-rich, low-A)

A/B substitution effects:

`delta_bal = ln(E2/E1) = 0.5031` (1.6538x)

`delta_D = ln(E4/E3) = 0.0870` (1.0909x)

Preregistered E6* hypotheses:

- **H_strong**: `E6* = E5 * E2/E1 = 44.65 Pa.s`
- **H_weak**: `E6* = E5 * E4/E3 = 29.45 Pa.s`

The separation is 1.516x. The equal-prior/equal-variance geometric midpoint is 36.27 Pa.s. Robust decision zones are frozen at <=33 Pa.s (weak-consistent), 33-40 Pa.s (indeterminate), >=40 Pa.s (strong-consistent).

These are **hypothesis anchors**, not claims that the historical patent point values are noise-free laboratory truth.

## Continuous mechanism statistic

After E6* measurement:

`theta = [ln(E6*/E5) - delta_D] / [delta_bal - delta_D]`

- theta = 0: D-rich-like A/B response
- theta = 1: balanced-like A/B response
- theta outside [0,1]: behavior stronger/weaker than either historical context

Theta replaces the old ratio-of-small-differences amplification metric as the primary continuous mechanism quantity.

## E6* formulation

E6* is the counterfactual partner of patent Example 9 at the level of reported nominal parts:

| A | B | C | D | PPG425 | tackifier | MDI |
|---:|---:|---:|---:|---:|---:|---:|
| 29.2 | 5.9 | 10.5 | 1.2 | 23.4 | 5.9 | 23.9 |

The polyester block remains 46.8 parts and the formulation totals 100.0 parts. Final MDI charge is recalculated from actual OH values and MDI NCO content.

## Material-equivalence claim ladder

Before synthesis, the Agent requires an auditable raw-material table.

- **ANCHOR_COMPATIBLE** - chemistry and disclosed property specifications support a patent-anchored prospective counterfactual interpretation.
- **SURROGATE_ONLY** - E6* remains a useful modern transfer experiment but cannot be described as exact historical completion.
- **AUDIT_REQUIRED** - critical identity/COA evidence is incomplete; no E6* decision is issued yet.
- **INCOMPATIBLE** - the Agent abstains from the historical absolute-viscosity hypothesis test.

Because the historical Hercules beta-pinene grade is not disclosed, manuscript language should prefer "patent-anchored prospective counterfactual" over "exact replication" unless documentary evidence improves.

## Prospective statistics

The primary endpoint is the geometric mean of **independent-batch** E6* prepolymer viscosities at 130 C, with at least three independent syntheses. Technical readings characterize instrument repeatability only.

Agent progression requires both:

1. point classification outside the 33-40 Pa.s no-decision zone; and
2. the batch-level 95% CI to remain outside the corresponding 33 or 40 Pa.s boundary.

Otherwise the Agent requests another E6* synthesis.

Always report theta and log Bayes-factor sensitivity across the frozen `sigma_log` grid 0.05/0.08/0.10/0.12/0.15.

## Secondary temperature-response analysis

Measure 110/120/130 C where practical and fit, per independent batch and stage:

`ln(eta) = a + b/T`

The Andrade slope `b` is a secondary physicochemical descriptor. It can show whether E6* precursor and prepolymer have different temperature sensitivity, but it does not replace the 130 C primary hypothesis test.

This specifically addresses a weakness of small polyurethane-viscosity datasets in which multiple temperatures from one formulation can create pseudo-replication: the inferential unit here remains the independent synthesis batch.

## Agent architecture

### Evidence / provenance tool
Retrieves source IDs, patent example locators, material specifications and COAs.

### Numerical model tool
Owns anchor effects, H_strong/H_weak predictions, theta, Bayes factors and any frozen v0.7 support metrics.

### Experiment policy tool
Chooses among `audit`, `run E6*`, `replicate E6*`, `rank transfer pool`, and `abstain`.

### Critic / gate tool
Rejects missing provenance, material incompatibility, insufficient independent batches and unsupported transfer.

The LLM does not own numerical scores and cannot override gates. This is intentionally different from an unconstrained "LLM proposes materials" system.

## Post-E6 closed loop

- Indeterminate or imprecise E6*: replicate E6*.
- Decisive E6*: freeze theta/mechanism state, then evaluate E7-E9 with the global support/uncertainty layer.
- No supported E7-E9 candidate: abstain.
- Supported transfer candidate: synthesize at most one next candidate as the second prospective experiment.

The second experiment is therefore conditional, not guaranteed. A defensible abstention is a publishable outcome of the policy.

## Main figure plan

1. **Evidence landscape and global falsification** - data provenance, v0.7 external tests, and 0/928 certification.
2. **Why abstention is necessary** - chemistry/temperature domain shift and uncertainty calibration.
3. **Structured historical anchor block** - E1-E5, missing E6* cell, H_strong/H_weak and theta.
4. **Auditable Agent policy** - material gate, E6* information gain, hard decision states and preregistration.
5. **Prospective E6* experiment** - independent batches, QC, 130 C result, theta/Bayes sensitivity; secondary Andrade response.
6. **Closed-loop update** - post-E6 Agent action: replicate, transfer candidate, or abstain; include second prospective result only if the policy legitimately selects one.

## Literature positioning

- Pugar et al., *Digital Discovery* (2025), DOI 10.1039/D5DD00287G: 39-prepolymer library; composition-based and physicochemical/Andrade models; highlights extrapolation tradeoffs and explicitly notes single-synthesis/pseudo-replication limitations. PUR-Bridge targets the next decision layer: external falsification, independent-batch prospective validation and experiment selection.
- Wang et al., *npj Computational Materials* (2026), DOI 10.1038/s41524-026-02136-4: LLM-based training-free active learning can reduce experiments in materials datasets. PUR-Bridge differs by separating LLM orchestration from numerical inference, enforcing provenance/material gates, allowing abstention, and tying the Agent to a preregistered HMPUR wet-lab counterfactual.

## Publication value if outcomes differ

- **E6* ~45 Pa.s**: supports transfer of the strong A/B effect into C-rich context.
- **E6* ~29-30 Pa.s**: supports weak-context transfer and falsifies the strong hypothesis.
- **E6* 33-40 Pa.s**: falsifies the forced binary story; demonstrates why the Agent must replicate/update rather than cherry-pick a mechanism.
- **Material gate fails**: the paper still retains a valuable negative conclusion about historical-data transfer, but the claim must pivot from patent-mechanism validation to modern surrogate design.

No branch of this outcome tree requires changing the preregistered thresholds after observing E6*.
