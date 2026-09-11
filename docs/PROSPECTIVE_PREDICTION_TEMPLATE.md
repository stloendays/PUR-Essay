# Prospective prediction / adjudication record — TEMPLATE ONLY

**Status: TEMPLATE. No prediction has been frozen by this file, and filling it in is a
human decision, not an automated one.**

This template exists so that *if* a genuinely pre-result prediction is later frozen, it is
frozen in a machine-readable shape with its timing recorded truthfully. It deliberately does
not contain any prediction.

## What this is not

- It is **not** a preregistration of anything that already exists in the repository.
- It does **not** modify the wet-lab experiment. The PPG2000 / STEPANPOL PDP-70 / 4,4'-MDI
  five-point, three-independent-batch design (`docs/VALIDATION_EXPERIMENT_V5.md`) has already
  started and is not to be redesigned to suit the Agent.
- It does **not** feed wet-lab data into PUR-RECOVER. Prospective measurements remain excluded
  from the primary benchmark input, in V1 and in V2 alike.

## The one rule that cannot be bent

`result_inspection_status` must be answered honestly **before** anything else is written.

| value | meaning | what may be claimed |
|---|---|---|
| `no_results_inspected` | no measurement for this claim has been seen by anyone writing the record | a genuinely prospective prediction |
| `some_results_inspected` | any measurement bearing on this claim has been seen | a **post hoc** analysis, labelled as such |
| `unknown` | it cannot be established who has seen what | a **post hoc** analysis, labelled as such |

If the value is anything other than `no_results_inspected`, the record is a retrospective
comparison. It may still be scientifically useful, and it must not be called preregistered.

Machine schema: `configs/prospective_adjudication_schema.json`.

## Fields to complete

```json
{
  "record_status": "DRAFT | FROZEN",
  "result_inspection_status": "no_results_inspected | some_results_inspected | unknown",
  "inspection_statement": "who has seen which measurements, and when, in plain language",
  "frozen_utc": "set only when record_status becomes FROZEN",
  "experiment": {
    "design_document": "docs/VALIDATION_EXPERIMENT_V5.md",
    "materials": ["PPG2000", "STEPANPOL PDP-70", "4,4'-MDI"],
    "n_formulations": 5,
    "n_independent_batches": 3,
    "design_changed_by_this_record": false
  },
  "provenance": {
    "git_commit": "", "config_sha256": "", "prompt_sha256": "",
    "pur_sim_v1_snapshot_sha256": "", "generated_by": "deterministic | agent | human"
  },
  "predictions": [
    {
      "id": "",
      "claim": "the directional or ordinal statement being predicted",
      "quantity": "canonical quantity name",
      "direction_or_ordering": "",
      "domain_of_validity": "the composition/temperature range in which the claim is meant to hold",
      "falsification_criterion": "the observation that would count as falsifying it, stated numerically",
      "measurement_procedure": "which measurement decides it",
      "adjudication": "pending | supported | partially_supported | falsified | out_of_domain",
      "adjudication_note": ""
    }
  ]
}
```

## Adjudication, once measurements exist

Each frozen claim is classified exactly once:

- **supported** — the observation meets the pre-stated criterion;
- **partially supported** — the direction holds but the stated bound or range does not;
- **falsified** — the pre-stated falsification criterion is met;
- **out of domain** — the measurement falls outside the declared domain of validity, so the
  claim is not tested by it.

Failed and falsified predictions are kept. A claim is never rewritten after adjudication, and
the Level-4-style boundary applies: a simulated ordering that survives a wet-lab comparison is
evidence about the ordering, not a released quantitative viscosity model.

## Relationship to PUR-RECOVER

The 928-candidate benchmark is an algorithmic decision benchmark on synthetic responses. It
is not empirical rheology evidence, and no wet-lab outcome changes its gold, tolerances or
metrics. Any Agent change motivated by a wet-lab result must be versioned separately and must
state that it was made after seeing that result.
