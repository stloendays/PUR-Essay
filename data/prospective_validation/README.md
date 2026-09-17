# data/prospective_validation

This directory now contains the executed wet-lab evidence for the local PPG2000/PDP-70/4,4'-MDI validation study and the subsequent formulation-correction loop.

## Scientific role

The wet-lab study is no longer treated as a future appendix-style check. It is the **primary experimental section of the manuscript**.

The evidence is interpreted in two stages:

1. **Prospective external wet-lab validation of the frozen formulation design.** The initial E1-E5 design was defined before these measurements were incorporated into the computational workflow. The measured temperature-viscosity response and 120 C hold data therefore test whether the computationally motivated design transfers to a real laboratory system.
2. **Closed-loop experimental correction.** The initial experiment exposed a strong time-dependent viscosity build-up and substantial run-to-run sensitivity. The corrected formulation partially replaces the all-reactive resin/polyol fraction with AC1920/TK100. Two repeat runs of the same corrected formulation then test whether the stability failure mode is suppressed reproducibly.

The second stage is deliberately called a closed-loop follow-up validation rather than a blind external validation, because the correction was chosen after observing the initial experimental failure mode.

## Current files

- `experimental_formulations_v1.csv` — E1-E5 formulation matrix plus the corrected formulation.
- `experimental_viscosity_v1.csv` — temperature sweeps, one-day retests, 120 C hold-stability measurements, and the two corrected-formulation repeat runs.
- `experimental_summary_v1.csv` — derived stability and repeatability metrics used in the manuscript.

The source sheet does not state a viscosity unit explicitly for every table. Raw values are therefore preserved without inventing a unit; manuscript figures must use the verified laboratory unit once confirmed from the instrument record.

## Main experimental findings supported by the supplied records

- Every recorded temperature sweep decreases monotonically from 80 to 130 C, confirming strong thermal dependence of the prepolymer viscosity.
- The repeated E2 runs span a max/min ratio of about 2.89 at 80 C and 3.57 at 120 C, exposing substantial process/run sensitivity in the original formulation.
- During a 120 C hold, E1 increases by 9.51% from 15 to 60 min and 16.85% from 15 to 90 min.
- During the same hold, E5 increases by 51.54% from 15 to 60 min and 93.08% from 15 to 90 min.
- The corrected formulation changes by -0.16% and +3.04% from 15 to 60 min in two repeat runs. Across the two repeats, pointwise CV values are about 2.87-5.11%.

The matched 15-60 min window is the fair comparison between the original and corrected formulations; the corrected formulation was not measured at 90 min in the supplied sheet.

## Mechanistic claim boundary

The experimental result directly supports **suppression of time-dependent viscosity build-up after formulation correction**. The proposed explanation — reducing the fraction of reactive components by adding petroleum/acrylate-type resin components — is treated as a formulation mechanism hypothesis consistent with the observed response, not as a directly proven reaction mechanism. No FTIR/NCO kinetic evidence is claimed.

## Relationship to the Agent benchmark

`agent_access = false` remains in force for this directory. Nothing here may be read by the primary blind Agent benchmark that defines recovery performance on the frozen computational decision. This prevents experimental answers from leaking into the benchmark.

The paper therefore keeps three evidence roles distinct while making wet-lab evidence the narrative centre:

```text
source-grounded/public evidence
        -> frozen computational design
        -> prospective wet-lab validation
        -> experimentally observed failure mode
        -> closed-loop formulation correction
        -> repeated wet-lab confirmation
        -> workflow update / stability-aware design objective

blind Agent benchmark = independent audit of recovery of the frozen computational decision
```

This organization allows the experiment to lead the materials-science story without contaminating the deterministic or blinded Agent evaluation.