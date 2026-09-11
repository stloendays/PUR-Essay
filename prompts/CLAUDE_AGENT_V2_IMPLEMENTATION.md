# Claude implementation prompt — PUR-RECOVER Agent Workflow V2

You are continuing development of the repository `stloendays/PUR-Essay`.

First pull the latest `main`, then read these files before making changes:

- `docs/AGENT_HANDOFF_CURRENT.md`
- `docs/AGENT_WORKFLOW_V2.md`
- `docs/AGENT_STRATEGY_V1.md`
- `configs/frontier_v1.json`
- `configs/recover_v1.json`
- `src/pur_agent/strategy.py`
- `src/pur_agent/runtime.py`
- `src/pur_agent/tools.py`
- `src/pur_agent/audit_tools.py`
- `src/pur_agent/schemas.py`
- `src/pur_agent/evaluator.py`
- `src/pur_agent/metrics.py`
- current tests under `tests/`

Context: a real-API pilot already exists under `results/recover_v1/pilot_20260910_b/` and commit `9dc5ae2`. The pilot showed:

- `direct_llm`: 0/3 complete recovery;
- `tool_llm`: 3/3;
- `pur_agent`: 3/3;
- `pur_agent_no_backward`: 2/2;
- `pur_agent_no_constraint_checker`: winners remained scientifically correct but one strict field failed because `mdi_fraction_min` and `mdi_fraction` are inconsistent names.

This means deterministic tools clearly help, but the current full Agent has not yet demonstrated an advantage over plain tool access. Your job is to implement a more scientifically distinctive Agent workflow without changing the frozen scientific answer.

## Non-negotiable invariants

Do NOT change any of the following:

- the 928-candidate PUR_SIM_V1 response table;
- `configs/frontier_v1.json` objective or constraints;
- L0/L1/L2 semantics;
- robust uncertainty rule;
- backward threshold definition;
- frozen evaluator gold;
- evaluator tolerances merely to improve model scores;
- blind-bundle isolation;
- wet-lab experiment design already in progress;
- existing pilot raw records.

Frozen evaluator-side science remains:

```text
L0 property winner      WO_INV_0419
L1 constrained winner   WO_INV_0579
L2 robust winner        WO_INV_0420
active boundary         MDI fraction >= 0.35
continuous threshold    NCO:OH = 1.7719836724
first reachable grid    NCO:OH = 1.8
```

The model-under-test must not see these source IDs or evaluator gold.

## Implement V2 as an additive/versioned path

Do not overwrite V1 behavior in a way that makes the old pilot irreproducible. Preserve existing conditions and add a separate `pur_agent_v2` path plus ablations.

Target workflow:

```text
PLAN -> SOLVE -> CHALLENGE -> CERTIFY -> EXPLAIN
```

### 1. Evidence planning

Implement a claim-evidence dependency structure for the final decision fields. Each final claim should have one or more admissible deterministic evidence paths. The planner/gate should verify minimum sufficient evidence rather than merely enforcing a hardcoded list of every tool.

At minimum support claims for:

- property winner;
- constrained winner;
- robust winner;
- active constraint;
- backward threshold;
- reachable grid value + reachability;
- NCO direction;
- composition direction.

The planning structure should be machine-readable and logged in each V2 run.

### 2. Deterministic solve

Continue to use existing deterministic `pur_science` primitives for numerical truth. Do not move numerical ranking/arithmetic into free-form LLM reasoning.

### 3. Challenge stage

Before finalization, require read-only scientific counterfactual challenge. Reuse existing `PUR-AUDIT V1` functionality where possible, especially:

- `constraint_counterfactual`;
- `uncertainty_counterfactual`;
- `consistency_report`.

The challenge stage should explicitly test:

- why L0 loses after constraints;
- why L1 loses under the robust rule;
- whether the current recommendation sits near a boundary/crossover;
- whether tool outputs contradict each other.

Challenge tools must not modify science or gold.

### 4. Dual-path verification

Turn the pilot's backward-tool redundancy into an explicit cross-check.

Implement two admissible threshold derivations when available:

- Path A: dedicated `solve_backward_threshold`;
- Path B: lower-level reconstruction using `local_nco_sweep` plus the relevant MDI-fraction calculation primitive.

Record both values, absolute difference, tolerance, and pass/fail. If they disagree beyond tolerance, the V2 Agent must surface a structured conflict rather than silently picking one.

### 5. Canonical constraint ontology

Fix the `mdi_fraction` vs `mdi_fraction_min` inconsistency before formal V2 runs using one canonical representation, preferably:

```json
{
  "quantity": "mdi_fraction",
  "operator": ">=",
  "threshold": 0.35
}
```

Use a shared helper/schema so tools, logs, V2 evaluator metrics and final outputs use consistent semantics. Keep scientific correctness and schema/interface correctness as separate diagnostics.

Do not retroactively alter old pilot records.

### 6. Deterministic decision certificate

Add a certificate builder derived from the trace rather than LLM self-reported confidence. Suggested fields:

```json
{
  "evidence_coverage": {"satisfied": 0, "required": 0},
  "cross_path_agreement": true,
  "constraint_audit_pass": true,
  "robustness_audit_pass": true,
  "schema_consistency_pass": true,
  "tool_contradictions": 0,
  "active_constraint_margin": null,
  "objective_margin": null,
  "certificate_pass": true
}
```

Where possible compute these deterministically from tool outputs and trace metadata. A free-form confidence field can remain only for backward compatibility; it is not the trust anchor.

### 7. Finalization gate

V2 may finalize only if:

- required claims have sufficient evidence;
- challenge stage completed;
- required cross-path checks passed or conflicts were explicitly surfaced;
- canonical ontology is respected;
- schema is valid;
- blind/gold/wet-lab separation is intact.

If evidence conflicts, return a structured conflict/abstention state instead of manufacturing consistency.

### 8. V2 conditions and ablations

Preserve existing conditions and add separately versioned conditions such as:

```text
pur_agent_v2
pur_agent_v2_no_evidence_planner
pur_agent_v2_no_challenge
pur_agent_v2_no_cross_path
pur_agent_v2_no_certificate
```

Do not assume these will help; they exist so the formal matrix can test which pieces matter.

### 9. Metrics

Keep `complete_decision_recovery` as the primary metric and add V2 diagnostics for:

- evidence coverage;
- cross-path agreement/failure;
- contradiction detection;
- scientific correctness vs interface/schema correctness;
- unnecessary tool-call count;
- total tool calls and LLM/API rounds;
- tokens, latency, cost if available;
- invalid output rate;
- abstention/conflict rate.

### 10. Prospective wet-lab separation

The current five-point PPG2000 / STEPANPOL PDP-70 / 4,4'-MDI experiment has already started. Do not change its design.

You may add a machine-readable prospective prediction/adjudication template only for predictions that are genuinely still pre-result. If a result has already been inspected, record that fact and do not call a retroactive prediction preregistered. Wet-lab observations remain excluded from primary PUR-RECOVER inputs.

## Tests required

Add or extend tests for:

- claim-evidence planner/gate;
- alternative evidence paths;
- cross-path threshold agreement and forced disagreement;
- canonical constraint ontology mapping;
- deterministic certificate construction;
- challenge-stage completion;
- structured conflict/abstention;
- no-gold leakage;
- V1 backward compatibility;
- V2 condition registration;
- evaluator metric separation between scientific and schema correctness.

Run the full test suite.

## Execution discipline

Before any real-API V2 run:

1. `git pull origin main`;
2. inspect current repo state and report any inconsistency;
3. implement small testable changes;
4. run `pytest -q`;
5. rebuild/verify frozen science and blind bundle if required by the existing workflow;
6. run leakage checks;
7. run mock V1 and V2 smoke tests;
8. only then run a small real-API V2 pilot;
9. do not start the 30-50 run formal matrix until code/prompt/config/data hashes and seed schedule are frozen.

Keep all failures. Do not delete bad runs, invalid JSON, timeouts, or transport failures.

## Deliverables

When done, report:

1. exact files changed;
2. concise architecture summary;
3. tests run and results;
4. mock smoke results;
5. any real-API pilot results if actually run;
6. any remaining scientific/interface caveats;
7. exact commit SHA pushed to GitHub;
8. commands for the next formal benchmark step.

Do not claim Agent superiority unless the repeated benchmark supports it.