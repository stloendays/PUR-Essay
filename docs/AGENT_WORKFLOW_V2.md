# PUR-RECOVER Agent Workflow V2 — post-pilot design note

**Status:** design specification after the real-API pilot. Implementation and formal benchmark reruns are still pending.

## 1. Why V2 exists

The first real-API pilot showed a clear separation between language-only reasoning and deterministic tool grounding, but it did **not** yet show an advantage of the full planning/gating layer over unrestricted tool access:

- `direct_llm`: 0/3 complete decision recovery;
- `tool_llm`: 3/3 complete recovery;
- `pur_agent`: 3/3 complete recovery;
- `pur_agent_no_backward`: 2/2 complete recovery;
- `pur_agent_no_constraint_checker`: correct winners but failed one strict audit field because of the `mdi_fraction` vs `mdi_fraction_min` naming inconsistency.

Therefore V2 must not add decorative complexity. Its purpose is to make the Agent scientifically distinctive **without changing the frozen decision result**.

## 2. Scientific invariants: do not change

V2 must preserve the current frozen scientific layer exactly:

```text
PUR_SIM_V1 candidate space: 928 candidates
L0 property winner:          WO_INV_0419
L1 constrained winner:       WO_INV_0579
L2 robust winner:            WO_INV_0420
active boundary:             MDI fraction >= 0.35
continuous NCO:OH boundary:  1.7719836724
first reachable grid point:  1.8
```

Do not change:

- candidate responses;
- `configs/frontier_v1.json` objective or constraints;
- uncertainty propagation or L2 admissibility;
- L0/L1/L2 semantics;
- evaluator tolerances to rescue a model;
- wet-lab design already in progress;
- primary blind-bundle separation from gold and prospective experimental data.

The 928-candidate benchmark remains an algorithmic/decision benchmark, not empirical rheology evidence.

## 3. V2 concept

The upgraded workflow is:

```text
PLAN -> SOLVE -> CHALLENGE -> CERTIFY -> EXPLAIN
```

The key distinction from V1 is that the Agent should no longer behave like a fixed checklist that merely proves every tool was called. It should construct a claim-evidence plan, obtain sufficient deterministic evidence, actively challenge the current decision, then issue a machine-auditable decision certificate.

## 4. Stage A — Evidence Planning

Before numerical decision work, the Agent builds an internal claim-evidence dependency graph.

Example:

```text
property_winner
  <- rank_property

constrained_winner
  <- rank_constrained
  <- constraint_audit

robust_winner
  <- rank_robust

backward_threshold
  <- solve_backward_threshold
  OR
  <- local_nco_sweep + calculate_mdi_fraction

nco_direction
  <- local_nco_sweep

composition_direction
  <- local_composition_sweep
```

The planner must identify the **minimum sufficient evidence** for every final claim. It may choose among admissible equivalent paths when more than one deterministic derivation exists.

This creates a real distinction between:

- `tool_llm`: has tools but no explicit claim-evidence planning/certification policy;
- `pur_agent_v2`: must satisfy the claim-evidence graph and certification contract.

## 5. Stage B — Deterministic Solve

Numerical truth remains tool-owned.

The Agent should recover:

1. L0 property winner;
2. L1 constrained winner;
3. L2 robust winner;
4. active constraint;
5. backward threshold;
6. reachable-grid projection;
7. local NCO trend;
8. local composition trend.

The LLM chooses the investigative sequence and interprets the outputs, but it should not perform 928-row arithmetic mentally when a deterministic primitive exists.

## 6. Stage C — Scientific Challenge

Before finalization, the Agent must attempt to falsify its own current recommendation using read-only counterfactual checks.

Minimum challenge questions:

1. Why does the L0 winner cease to be preferred after nominal constraints?
2. Why does the L1 winner cease to be preferred under the frozen robust rule?
3. Is the selected robust winner close to a decision boundary or objective crossover?
4. Are any tool outputs mutually inconsistent?

Reuse existing `PUR-AUDIT V1` primitives where possible rather than inventing new science:

- `constraint_counterfactual`;
- `uncertainty_counterfactual`;
- `consistency_report`;
- optionally `weight_stability` / `pareto_alternatives` as secondary diagnostics.

Challenge tools are not permitted to alter the frozen scientific result. They only test whether the Agent can explain and audit the same decision.

## 7. Stage D — Dual-path verification

The pilot showed that the backward threshold can be recovered without the dedicated backward tool by combining lower-level deterministic primitives. V2 should turn this into an explicit robustness feature rather than treating it as accidental redundancy.

For critical quantities with two admissible derivations, compute both and compare:

```text
Path A: solve_backward_threshold
Path B: local_nco_sweep + calculate_mdi_fraction
```

Then record:

```text
cross_path_verified = true/false
absolute_difference = ...
tolerance = ...
```

If paths disagree beyond the predeclared tolerance, the Agent should flag a contradiction rather than silently choose the preferred answer.

This is intended as **independent scientific reconstruction**, not majority voting between LLM outputs.

## 8. Stage E — Canonical scientific ontology

The pilot exposed `mdi_fraction` versus `mdi_fraction_min` as an interface naming inconsistency rather than a scientific reasoning error.

Before formal V2 runs, freeze a canonical constraint representation such as:

```json
{
  "quantity": "mdi_fraction",
  "operator": ">=",
  "threshold": 0.35
}
```

All tools, schemas, logs, evaluator outputs and manuscript terminology should map to this canonical object.

Keep separate metrics for:

- scientific correctness;
- interface/schema correctness.

Any ontology change must be made before the V2 formal matrix and applied to all conditions, not patched after seeing model results.

## 9. Stage F — Decision Certificate

Replace or supplement free-form LLM confidence with a machine-auditable certificate derived from observed evidence.

Suggested certificate fields:

```json
{
  "evidence_coverage": {"satisfied": 9, "required": 9},
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

The certificate should be deterministically computed from the trace where possible. A free-form scalar `confidence` may remain for compatibility, but it must not be the primary trust signal.

## 10. Finalization policy

The V2 Agent may finalise only when:

- every required claim has sufficient evidence;
- challenge stage has executed;
- all required cross-path comparisons are within tolerance, or contradictions are explicitly surfaced;
- canonical constraint ontology is respected;
- output schema is valid;
- wet-lab data and evaluator gold have not entered the model-under-test context.

If these conditions fail, the Agent should return a structured conflict/abstention state instead of manufacturing consistency.

## 11. Prospective wet-lab adjudication

The current five-point PPG2000 / STEPANPOL PDP-70 / 4,4'-MDI experiment is already in progress and must not be redesigned to fit the Agent.

Before any wet-lab result is used to modify the Agent, freeze a prospective prediction/adjudication record containing only pre-result claims that are genuinely already specified, for example:

- expected NCO-direction ordering;
- expected composition-direction sign;
- expected pre-MDI -> post-MDI rheological amplification pattern;
- explicit falsification criteria;
- exact git/config/prompt hashes used when the predictions were generated.

After measurements are available, the Agent may compare frozen predictions with observations and classify each claim as supported / partially supported / falsified / out-of-domain. Wet-lab results remain excluded from the primary PUR-RECOVER benchmark input.

If any experimental result has already been inspected, do not retroactively call a newly written prediction preregistered. Mark timing and provenance truthfully.

## 12. Benchmark design after implementation

Do not assume V2 is better. Test it.

Core comparison should include:

```text
direct_llm
tool_llm
pur_agent_v1 or single-pass planning baseline
pur_agent_v2
```

Recommended V2 ablations:

```text
v2_no_evidence_planner
v2_no_challenge
v2_no_cross_path
v2_no_certificate
```

Primary metric remains complete decision recovery. Add diagnostics for:

- evidence coverage;
- contradiction detection;
- cross-path agreement;
- scientific correctness vs schema correctness;
- unnecessary tool calls;
- total tool calls/API rounds;
- input/output tokens;
- latency and cost;
- invalid output rate.

Formal claims require the same predeclared run count and seed schedule across comparable conditions.

## 13. What would count as a meaningful Agent-specific advantage

V2 does not need to beat `tool_llm` only on Top-1 accuracy. Its value can appear as any predeclared combination of:

- higher complete-chain recovery;
- lower schema/interface error;
- better contradiction detection;
- fewer unnecessary tool calls for the same evidence coverage;
- more stable explanation fidelity;
- valid abstention when evidence conflicts;
- better reproducibility across seeds.

If `tool_llm` and V2 remain statistically indistinguishable after adequate repeated runs, report that result rather than manufacturing an Agent advantage. The paper can still support the stronger claim that deterministic scientific tooling converts an unreliable language-only baseline into a reproducible decision system.

## 14. Implementation rule

Prefer small, testable extensions to the existing codebase:

- extend `src/pur_agent/strategy.py` with claim-evidence planning and challenge/certificate gates;
- reuse `src/pur_agent/audit_tools.py` counterfactual primitives;
- add a deterministic certificate builder rather than letting the LLM invent certificate values;
- normalize the constraint ontology in one shared schema/helper;
- extend run JSON and evaluator metrics without changing frozen science;
- add unit tests for every new gate and ontology mapping;
- version new benchmark outputs separately from the existing pilot records.

Do not rewrite `pur_science` unless a genuine scientific-contract bug is independently demonstrated.

## 15. Paper-facing framing

The upgraded paper framing should be:

> Even when the underlying numerical operations are individually straightforward, a language model does not reliably preserve a multi-stage scientific decision chain. The proposed workflow combines claim-level evidence planning, deterministic scientific tools, active counterfactual challenge, independent cross-path verification, and machine-auditable decision certification to make the recovered decision reproducible and inspectable.

This framing is intentionally narrower and more defensible than claiming that the PUR optimization itself is computationally difficult.
