# data/prospective_validation

This directory contains the executed wet-lab records used for the experimental validation layer.

## Scientific role

The current paper uses a **human-in-the-loop Agent-guided validation** architecture:

```text
computational / source evidence
-> chemistry + process-state uncertainty
-> Agent recommendation
-> frozen recommendation
-> human wet-lab execution
-> physical measurement
-> adjudication
```

The Agent is not a physical actuator. It may evaluate uncertainty and recommend formulation/measurement points; human operators synthesize the material, impose the thermal history, and perform rheology measurements.

## Process-state variables

The next design layer explicitly carries:

```text
reaction_history
thermal_hold_time
preparation_perturbation
```

These are known process-relevant variables. The present measurements quantify their importance in this system so that they can be represented explicitly rather than being absorbed into an undifferentiated error term.

## Current files

- `experimental_formulations_v1.csv` — E1-E5 plus the supplied follow-up formulation.
- `experimental_viscosity_v1.csv` — temperature-sweep, thermal-hold, repeat and one-day observations transcribed from the supplied experiment sheet.
- `experimental_summary_v1.csv` — derived stability/repeatability summaries used in the manuscript.

## Agent-validation terminology

A measured point may be described as **prospective physical validation/adjudication of an Agent recommendation** only if the recommendation was frozen before that point's result was inspected.

The final manuscript should therefore pair the final repeated wet-lab result with an immutable pre-result recommendation record containing at least:

```text
recommendation_id
recommended formulation / condition
uncertainty or decision rationale
acceptance or falsification criterion
generation timestamp
git commit or run ID
result_inspection_status
human execution reference
```

The schema for new recommendation records is `../../configs/agent_experiment_recommendation_v1.schema.json`.

Do not fabricate a preregistration after seeing results. If the relevant historical recommendation trace exists, attach it as provenance; if chronology cannot be demonstrated, describe the measurement as closed-loop follow-up evidence rather than prospective Agent validation.

## Separation from PUR-RECOVER

These data remain excluded from the primary blind PUR-RECOVER Agent benchmark. PUR-RECOVER audits recovery of the frozen deterministic decision chain; this directory contains physical experimental evidence.

The two evidence lines may be discussed in the same paper, but they must not leak into each other's gold/input definitions.
