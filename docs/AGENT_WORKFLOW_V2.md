# PUR-RECOVER Agent Workflow V2 — post-pilot design note

**Status (2026-09-17):** PUR-RECOVER V2 remains the blinded decision-recovery benchmark. The paper now additionally contains a separately versioned **experimental recommendation Agent** (`docs/AGENT_EXPERIMENT_INTERFACE_V1.md`) that may recommend wet-lab points under uncertainty while human operators execute them. Do not conflate that application layer with PUR-RECOVER.

## 1. Why V2 exists

The first real-API pilot showed a clear separation between language-only reasoning and deterministic tool grounding, but it did not yet show an advantage of the full planning/gating layer over unrestricted tool access:

- `direct_llm`: 0/3 complete decision recovery;
- `tool_llm`: 3/3 complete recovery;
- `pur_agent`: 3/3 complete recovery;
- `pur_agent_no_backward`: 2/2 complete recovery;
- `pur_agent_no_constraint_checker`: correct winners but failed one strict audit field because of the `mdi_fraction` vs `mdi_fraction_min` naming inconsistency.

Therefore V2 must not add decorative complexity. Its purpose is to make the **blind recovery task** scientifically auditable without changing the frozen decision result.

## 2. Scientific invariants

PUR-RECOVER V2 preserves:

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
- primary blind-bundle separation from gold and wet-lab data.

The 928-candidate benchmark remains an algorithmic/decision benchmark, not empirical rheology evidence.

## 3. V2 concept

```text
PLAN -> SOLVE -> CHALLENGE -> CERTIFY -> EXPLAIN
```

PUR-RECOVER builds a claim-evidence plan, obtains deterministic evidence, challenges the recovered decision, and issues a machine-auditable certificate.

## 4. Evidence planning

The Agent builds a claim-evidence dependency graph. Example:

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
```

The planner identifies minimum sufficient evidence for each final claim.

## 5. Deterministic solve

Numerical truth remains tool-owned. PUR-RECOVER should recover:

1. L0 property winner;
2. L1 constrained winner;
3. L2 robust winner;
4. active constraint;
5. backward threshold;
6. reachable-grid projection;
7. local NCO trend;
8. local composition trend.

## 6. Scientific challenge

Before finalization, the Agent attempts to falsify its recovered recommendation using read-only counterfactual checks:

- why L0 ceases to be preferred after nominal constraints;
- why L1 ceases to be preferred under the robust rule;
- whether the robust winner is close to a boundary/crossover;
- whether tool outputs are mutually consistent.

Challenge tools do not alter the frozen scientific result.

## 7. Dual-path verification

For critical quantities with two admissible derivations, compute both and compare. Example:

```text
Path A: solve_backward_threshold
Path B: local_nco_sweep + calculate_mdi_fraction
```

Disagreement beyond tolerance is surfaced as a contradiction rather than silently resolved.

## 8. Canonical scientific ontology

Use a canonical constraint object such as

```json
{
  "quantity": "mdi_fraction",
  "operator": ">=",
  "threshold": 0.35
}
```

Keep scientific correctness separate from interface/schema correctness.

## 9. Decision certificate

The certificate is deterministically derived from the trace where possible and may include:

```json
{
  "evidence_coverage": {"satisfied": 9, "required": 9},
  "cross_path_agreement": true,
  "constraint_audit_pass": true,
  "robustness_audit_pass": true,
  "schema_consistency_pass": true,
  "tool_contradictions": 0,
  "certificate_pass": true
}
```

## 10. Finalization policy

PUR-RECOVER may finalise only when required evidence is covered, challenge/cross-path checks are complete, ontology/schema rules are respected, and wet-lab/gold leakage has not occurred.

If not, return a structured conflict/abstention state.

## 11. Relationship to wet-lab recommendation

The current paper now has a separate experimental application path:

```text
chemistry + process-state uncertainty
-> experimental recommendation Agent
-> frozen recommendation
-> human wet-lab execution
-> physical adjudication
```

The process-state block currently includes:

```text
reaction_history
thermal_hold_time
preparation_perturbation
```

This application is **not PUR-RECOVER**. The experimental Agent may recommend points; PUR-RECOVER remains the blind audit benchmark. Wet-lab outcomes remain excluded from PUR-RECOVER inputs and cannot change its frozen gold.

For any claim that a final experiment prospectively validates an Agent recommendation, preserve a pre-result recommendation record using `configs/agent_experiment_recommendation_v1.schema.json`.

## 12. Benchmark design

Core comparison:

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

Primary metric remains complete decision recovery. Add diagnostics for evidence coverage, contradiction detection, cross-path agreement, schema correctness, tool calls, tokens, latency, cost, and invalid output rate.

## 13. Meaningful PUR-RECOVER-specific advantage

Useful evidence may include:

- higher complete-chain recovery;
- lower schema/interface error;
- better contradiction detection;
- fewer unnecessary calls for the same evidence coverage;
- more stable explanation fidelity;
- valid abstention when evidence conflicts;
- better reproducibility across seeds.

If `tool_llm` and V2 remain statistically indistinguishable, report that result.

## 14. Implementation rule

Prefer small, testable extensions to the existing codebase. Do not modify frozen science merely to improve Agent benchmark performance.

## 15. Paper-facing framing

PUR-RECOVER claim:

> Deterministic scientific tools plus evidence planning, challenge, cross-path verification, and certification make a multi-stage formulation decision reproducible and inspectable.

Experimental application claim:

> An uncertainty-aware Agent can recommend experimentally useful formulation/measurement points without physical actuation; human-executed wet-lab measurements then prospectively adjudicate those recommendations when chronology is frozen before measurement.

These are complementary claims, not the same task.

## 16. Preserved implementation record

V1 conditions, prompts, tool outputs, blind bundle and pilot records remain immutable. New experimental recommendation code/data must be versioned separately and must not overwrite historical PUR-RECOVER evidence.
