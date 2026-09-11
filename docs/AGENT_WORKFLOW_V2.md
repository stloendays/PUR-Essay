# PUR-RECOVER Agent Workflow V2 — post-pilot design note

**Status (2026-09-11):** implemented and green under mock; the real-API V2 pilot and the formal matrix are still pending. Section 16 records where each part of this specification now lives in code, and what it does *not* yet establish.

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

## 16. Implementation record (2026-09-11)

Implemented additively. V1 conditions, prompts, tool outputs, blind bundle and pilot records are byte-unchanged; `pytest -q` is 129 passed.

| Spec section | Implementation | Notes |
|---|---|---|
| 4 — evidence planning | `src/pur_agent/evidence.py` | 9 claims, each with one or more admissible paths; ablated paths become `unsatisfiable` rather than failed |
| 5 — deterministic solve | unchanged `pur_science` via `src/pur_agent/tools.py` | no numerical logic moved into the LLM |
| 6 — challenge | `src/pur_agent/challenge_tools.py` | thin wrappers over the frozen `pur_science.depth` primitives already used by PUR-AUDIT V1 |
| 7 — dual-path verification | `src/pur_agent/crosspath.py` | both values reconstructed **from the recorded trace**, not from the model's prose |
| 8 — canonical ontology | `src/pur_agent/ontology.py`, `src/pur_agent/tools_v2.py` | the V2 tool outputs stop emitting `mdi_fraction_min` |
| 9 — decision certificate | `src/pur_agent/certificate.py` | deterministic; never returned to the model |
| 10 — finalisation gate | `V2Policy` in `src/pur_agent/strategy.py` | procedural only, see below |
| 12 — conditions | `src/pur_agent/conditions.py` | `pur_agent_v2` plus four ablations |
| 12 — metrics | `score_decision_v2` in `src/pur_agent/metrics.py` | primary metric unchanged |
| 11 — wet-lab separation | `docs/PROSPECTIVE_PREDICTION_TEMPLATE.md`, `configs/prospective_adjudication_schema.json` | template only; no prediction frozen |

### The challenge tools are claim-driven, not chain-returning

`audit_tools.py` (PUR-AUDIT V1) returns the deterministic decision chain, which is correct for an audit task whose job is not to find the winners. In recover mode that would be a shortcut to the answer the challenge is supposed to interrogate. The V2 wrappers therefore take the Agent's **own asserted claims** as arguments and return a verdict on them: `challenge_consistency` runs the frozen consistency checks against the chain the Agent is about to submit, and `challenge_constraint_relaxation` reports whether the *claimed* constrained winner is the winner at the frozen floor instead of naming the actual one. `consistency_report`'s detail string, which names the true global property minimiser, is redacted in the V2 wrapper.

### The gate is procedural, and that is a hard constraint

The finalisation gate's corrective message is fed back into the model's context. Anything in it that depends on the answer being right would be a gold side-channel. The live gate therefore checks only: evidence coverage, challenge completion, cross-path surfacing, output schema, canonical vocabulary. Feasibility of the claimed winners, the active-constraint margin and the objective margin are computed in the certificate **after** the run and are never sent back. `tests/test_agent_v2.py::test_gate_feedback_carries_no_correctness_information` asserts this on the recorded gate attempts.

The certificate also deliberately does not check rank optimality. "Is this the best candidate?" is evaluator territory; a certificate that encoded it would be a disguised oracle.

### Known confounds for the V2 comparison

These must be stated in the paper rather than argued away:

1. **Gate feedback inflates schema correctness.** The V2 gate returns a non-canonical spelling to the model for correction, so V2's schema-correctness advantage over `tool_llm` is partly produced by the gate itself. `first_answer_gate_clean_rate` and `gate_retries_mean` are recorded per run so the pre-correction figure is reported alongside the post-correction one.
2. **The challenge tools add ways to see the winners.** They are deterministic functions of the same blind table, and every V2 condition already has `rank_property` / `rank_constrained` / `rank_robust`, which return the winners directly — so the marginal information is a smaller call count, not new knowledge. It is still an asymmetry against `tool_llm` and should be reported as one.
3. **Mock results prove plumbing, not science.** The mock is a perfect tool-follower, so every V2 condition scores 1.0 under it. Gating ablations can only show an effect against a real model.

### What V2 does not yet establish

Nothing about whether planning and gating beat plain tool access. That needs the real-API pilot and then the formal matrix at a predeclared run count. If `tool_llm` and `pur_agent_v2` remain indistinguishable, section 13 applies: report it.

*Partly answered by §17. The pilot has since run: the gates showed nothing measurable, the ontology showed something. Section 13 is being applied to the gating layer.*

## 17. Real-API V2 pilot result (2026-09-11)

Model `gpt-5.6-luna` via a local OpenAI-compatible proxy (Chat Completions; the endpoint does
not serve the Responses API). 3 runs per condition, seeds 3001-3003, commit `beb5927`, manifest
`results/recover_v2/pilot_v2_20260911/run_manifest.json` (`baf31dac…`), frozen on a clean
worktree **before** the runs. All 24 runs are preserved. **This is a pilot: n=3 per condition,
no statistical claim is made, and nothing was tuned on it.**

| condition | complete | certificate | coverage | cross-path | challenge | tools | API | input tok | latency | gate retries |
|---|---|---|---|---|---|---|---|---|---|---|
| `direct_llm` | **0/3** | – | – | – | – | 0 | 1 | 49 388 | 98.9 s | – |
| `tool_llm` | **2/3** | – | – | – | – | 9 | 10 | 52 538 | 37.2 s | – |
| `pur_agent` | 3/3 | – | – | – | – | 9 | 10 | 54 070 | 36.8 s | – |
| `pur_agent_v2` | 3/3 | 3/3 | 1.00 | 3/3 | 3/3 | 14.7 | 15.7 | 155 044 | 77.2 s | **0** |
| `..._no_evidence_planner` | 3/3 | 3/3 | 1.00 | 3/3 | 3/3 | 14.3 | 15.3 | 151 887 | 81.0 s | 0 |
| `..._no_challenge` | 3/3 | 3/3 | 1.00 | 3/3 | n/a | 10.7 | 11.7 | 106 108 | 65.1 s | 0 |
| `..._no_cross_path` | 3/3 | 3/3 | 1.00 | 3/3 | 3/3 | 15.0 | 16.0 | 178 045 | 78.2 s | 0 |
| `..._no_certificate` | 3/3 | 3/3 | 1.00 | 3/3 | 3/3 | 14.7 | 15.7 | 166 454 | 80.7 s | 0 |

0 transport/API errors, 0 invalid outputs, 0 abstentions or conflicts. Cross-path absolute
difference was exactly `0.0` in all 15 V2 runs; both derivations returned `1.771983672436161`.

### What the pilot does support

**The canonical ontology earned its place.** `tool_llm` run 2 recovered every winner, the
threshold, the grid point, reachability and both trends correctly, then failed the primary
metric on one field: it wrote `active_constraint.name = "mdi_fraction_min"`, copied from the V1
tool's own `solve_backward_threshold.constraint` output. Splitting the metric makes this legible:

| condition | scientifically correct | canonical spelling |
|---|---|---|
| `tool_llm` | 3/3 | **2/3** |
| `pur_agent` | 3/3 | 3/3 |
| `pur_agent_v2` (all five variants) | 3/3 | 3/3 |

This is the same defect the V1 pilot saw in `pur_agent_no_constraint_checker`, now reproduced in
a *baseline* rather than an ablation. V2 removes it at source: the V2 toolbox no longer emits
`mdi_fraction_min`, so there is nothing to miscopy. The fix is in the tool interface, not in the
evaluator — the strict primary metric still fails on a legacy spelling, by design.

### What the pilot does not support

**The gating layer demonstrated nothing measurable.** `gate_retries = 0` in all 15 V2 runs and
`first_answer_gate_clean_rate = 1.0`: the model satisfied the evidence contract, ran the
challenge and produced canonical, schema-valid JSON on its first answer every time. A gate that
never fires cannot show an effect, which is exactly why all four gate ablations also scored 3/3.
`no_evidence_planner`, `no_cross_path` and `no_certificate` are, at this sample size and with
this model, indistinguishable from the full contract.

That is a real negative result for the planning/gating layer and is reported as one. It also
means the V2 schema advantage in this pilot came from the **ontology**, not from gate feedback —
a cleaner attribution than the confound anticipated in §16, and one that should be re-checked
with a weaker model, where the gate is more likely to bind.

### Confounds that remain

1. **No condition isolates the ontology.** Every V2 condition uses the V2 toolbox, so all five
   inherit the fix. The closest available contrast is `no_certificate` (V2 toolbox, no machine
   gate at all: 3/3) against `tool_llm` (V1 toolbox, no gate: 2/3) — but those also differ in
   prompt. A `tool_llm_v2_ontology` condition (V2 toolbox, V1-style prompt, no gate) would
   isolate it and is the single most informative condition to add before the formal matrix.
2. **Cost.** V2 spends ~3x the input tokens and ~2x the latency of `tool_llm` for the same
   primary-metric outcome. Whatever V2 is worth, it is not free, and the trade should be stated
   in those terms.
3. **The challenge tools still widen the information surface**, as noted in §16.
4. **Ceiling effect.** `gpt-5.6-luna` is at or near ceiling on this task with tools. Separating
   `tool_llm` from `pur_agent_v2` may require a weaker model, a harder variant, or a run count
   large enough to resolve a low failure rate.
