# Prospective prediction / adjudication record — LEGACY FIXED-DESIGN TEMPLATE

**Status: TEMPLATE. No prediction has been frozen by this file.**

This template is retained for the earlier case in which an experiment was already fixed and an Agent/human froze predictions about that unchanged design. It is **not** the schema for the new uncertainty-aware experimental recommendation layer.

For an Agent that actually recommends formulation or measurement points, use:

- `docs/AGENT_EXPERIMENT_INTERFACE_V1.md`
- `configs/agent_experiment_recommendation_v1.schema.json`

## What this template is for

Use it only when:

```text
experimental design already fixed
-> prediction made about that fixed experiment
-> design_changed_by_this_record = false
```

It does not feed wet-lab data into PUR-RECOVER. Wet-lab measurements remain excluded from the primary blind benchmark input.

## Chronology rule

`result_inspection_status` must be recorded truthfully before a claim is called prospective.

| value | meaning | claim status |
|---|---|---|
| `no_results_inspected` | the relevant measurement has not been inspected | prospective prediction is permitted |
| `some_results_inspected` | any relevant result has already been inspected | post hoc only |
| `unknown` | chronology cannot be established | post hoc only |

Machine schema: `configs/prospective_adjudication_schema.json`.

## Legacy fields

```json
{
  "record_status": "DRAFT | FROZEN",
  "result_inspection_status": "no_results_inspected | some_results_inspected | unknown",
  "inspection_statement": "who has seen which measurements, and when",
  "frozen_utc": "set only when record_status becomes FROZEN",
  "experiment": {
    "design_document": "<fixed design document>",
    "materials": ["..."],
    "n_formulations": 1,
    "n_independent_batches": 1,
    "design_changed_by_this_record": false
  },
  "provenance": {
    "git_commit": "",
    "config_sha256": "",
    "prompt_sha256": "",
    "pur_sim_v1_snapshot_sha256": "",
    "generated_by": "deterministic | agent | human"
  },
  "predictions": [
    {
      "id": "",
      "claim": "",
      "quantity": "",
      "direction_or_ordering": "",
      "domain_of_validity": "",
      "falsification_criterion": "",
      "measurement_procedure": "",
      "adjudication": "pending",
      "adjudication_note": ""
    }
  ]
}
```

## Current recommendation architecture

The current manuscript instead allows:

```text
chemistry + process-state uncertainty
-> Agent recommendation
-> frozen recommendation
-> human wet-lab execution
-> physical adjudication
```

where the process-state block includes reaction history, thermal hold time, and preparation perturbation.

Do not force this new recommendation history into the legacy `design_changed_by_this_record = false` schema. Use the new recommendation schema so the Agent recommendation is explicit and auditable.

## Relationship to PUR-RECOVER

The experimental recommendation task and PUR-RECOVER remain separate. PUR-RECOVER evaluates blind recovery of the frozen deterministic benchmark. The recommendation task evaluates whether an uncertainty-aware recommendation survives physical human-executed testing. Neither task is allowed to redefine the other's gold after results are observed.
