# PUR-RECOVER V1 Agent strategy

## Current status correction (2026-09-10)

The earlier repository audit that described the complete 928-row `PUR_SIM_V1` response table as missing is superseded. The historical archive was re-audited, the distinct 928 x 51 deterministic `PUR_SIM_V1` table was recovered, and its canonical 14-column projection reproduces the repository frozen snapshot SHA256 exactly:

```text
d8623116c6a2f60c9e022e52eeb6540573dd9434b5e507c79701abb55635bcd9
```

Therefore the current Agent benchmark **retains the 928-candidate PUR_SIM_V1 decision space**. Its role is strictly algorithmic/decision benchmarking; it is not empirical evidence for real PUR rheology.

The current L2 rule must be inherited from `configs/frontier_v1.json`: propagated uncertainty intervals are required to remain inside the **broad functional windows**, not the preferred windows; `domain_ratio <= 1.0`; then the exact worst-case value of the same frozen log-space objective is minimized. Preferred windows define the optimization target, not the robust certification envelope.

## Design principle

The Agent is a **blinded scientific decision-recovery system**, not an optimizer that owns the answer. The deterministic science layer (PUR-FRONTIER V1) is frozen first; the Agent is evaluated afterwards.

```text
Deterministic science -> freeze gold -> hide answer -> Agent gets admissible data
  -> Agent reasons / uses tools -> Evaluator compares Agent result to frozen gold
```

Current evaluator-side scientific gold is:

```text
L0 property winner      WO_INV_0419
L1 constrained winner   WO_INV_0579
L2 robust winner        WO_INV_0420
active constraint       MDI fraction >= 0.35
backward threshold      NCO:OH = 1.7719836724
first reachable grid    NCO:OH = 1.8
```

These source IDs are never exposed to the anonymised primary Agent bundle.

## What the Agent sees / does not see

Sees (inside `benchmark/recover_v1/blind/` only): anonymised candidate table containing all admissible descriptors and responses, the frozen public scientific config, task statement/provenance block and deterministic tools.

Never sees: source candidate IDs, gold IDs, oracle ranks/scores/best flags, ordered ranking lists, mapping files, evaluator files, `results/`, or `data/prospective_validation/`. This is enforced by the filesystem guard, leakage scanner and tests.

## Strategy stack

1. **Anonymisation** — seed-fixed mapping of candidate IDs (`Candidate_0001...`) and polyols (`Polyol_A...`); mapping is evaluator-side only. A secondary named-chemistry benchmark tests domain priors.
2. **Deterministic tool grounding** — arithmetic, L0/L1/L2 ranking, feasibility, backward solving, reachability and local sweeps are Python tools delegating to `pur_science`; the LLM plans and interprets rather than doing 928-row mental arithmetic.
3. **Staged plan / evidence reconciliation** — the full Agent follows `inspect -> property rank -> constrain -> robust rank -> backward -> local sweep -> verify -> final` rather than a single-pass answer. Numerical truth remains tool-owned.
4. **Complete-decision recovery** — property winner, constrained winner, robust winner, active constraint, backward threshold, reachable grid value, reachability verdict, NCO direction and composition direction. A lucky top-1 guess is not a complete success.
5. **Trace gating** — the full Agent cannot finalise until required deterministic tool families have been inspected; ablations remove both the tool and its trace requirement so failures remain measurable rather than impossible to execute.
6. **Structured self-check** — before finalisation, the Agent reconciles its candidate IDs, feasibility state, robust result, backward threshold/grid projection and local trends against its own deterministic tool trace. Self-check may catch internal inconsistency but may not inspect evaluator gold.
7. **Robustness recovery** — the primary benchmark uses the frozen PUR-FRONTIER V1 robust rule. `rank_robust` must return an L2 winner. Explicit robustness abstention remains only a safety behavior for a different/unfrozen config and is not the expected current result.
8. **Independent evaluation** — `complete_decision_recovery` is the primary metric; component metrics diagnose why a run succeeds or fails.
9. **Immutable failure-aware runs** — invalid schema, wrong science, timeouts, transport errors and other failed formal runs remain part of the raw evidence and feed a declared failure taxonomy.
10. **Wet-lab separation** — prospective measurements remain excluded from the primary benchmark. The current wet-lab source of truth is `docs/VALIDATION_EXPERIMENT_V3.md`, but its candidate identities/results are not Agent inputs.

## Frozen robust task

The Agent inherits `configs/frontier_v1.json` rather than a duplicate scoring definition. The current L2 task requires:

- nominal L1 feasibility first;
- propagated uncertainty interval inside **broad functional windows**;
- `domain_ratio <= 1.0`;
- exact worst-case objective with log10-radius multipliers `(1, 1, 2)` for eta80, eta120 and eta80/eta120;
- `require_interval_inside_preferred = false`.

The LLM is not allowed to introduce new uncertainty weights or modify the frontier after seeing the gold.

## Conditions

| Condition | Tools | Strategy guard | Role |
|---|---|---|---|
| `oracle` | — | — | deterministic gold reference |
| `direct_llm` | none | no | pure language baseline |
| `tool_llm` | all | no | tools without full strategy enforcement |
| `pur_agent` | all | yes | inspect -> rank -> constrain -> robust rank -> backward -> local sweep -> self-check -> final |
| `pur_agent_no_backward` | minus backward/reachability | yes | ablation |
| `pur_agent_no_constraint_checker` | minus constraint audit / constrained & robust ranking | yes | ablation |
| `pur_agent_no_provenance` | all | yes | provenance ablation |
| `pur_agent_single_pass` | all | no | planning/trace-enforcement ablation |

Negative results are kept; no condition is retuned after formal runs begin.

## Primary evaluation

A run is counted as `complete_decision_recovery = true` only when the required decision chain is recovered within the frozen tolerances. Diagnostic metrics include:

- Top-1/Top-3/Top-5 recovery;
- recovered oracle rank and objective regret;
- hard-constraint violations;
- backward-threshold error;
- reachability accuracy;
- explanation fidelity;
- tool-call count, API calls, token usage and latency;
- invalid schema/JSON rate;
- API/transport failure rate;
- failure category.

Formal performance claims require repeated real-API runs. Mock runs are infrastructure tests only.

## Output schema

```json
{
  "property_winner": "Candidate_XXXX",
  "constrained_winner": "Candidate_XXXX",
  "robust_winner": "Candidate_XXXX",
  "robust_abstention_reason": null,
  "active_constraint": {"name": "...", "threshold": 0.0, "candidate_value": 0.0, "evidence": "..."},
  "backward_design": {"variable": "nco_oh", "continuous_threshold": 0.0, "nearest_reachable_grid_value": 0.0, "reachable": true, "active_constraint": "..."},
  "local_trends": {"nco_direction": "...", "composition_axis": "...", "composition_direction": "...", "notes": "..."},
  "evidence": [],
  "final_reasoning_summary": "...",
  "confidence": 0.0,
  "abstain": false,
  "abstention_reason": null
}
```

## Formal-run discipline

Before large repeated API runs, freeze a preregistration-style run manifest containing the exact git commit, prompt/config/data hashes, recovered 928 snapshot hash, anonymisation seed, model/provider identifiers, seed schedule, run count, max rounds, tool policy, evaluator tolerance and retry/failure policy.

Comparable conditions should use the same predeclared run count and seed schedule. Raw run JSON is immutable evidence. If a genuine scientific-contract bug is discovered after formal execution begins, version the benchmark and rerun all affected conditions instead of silently patching the current results.

## Run records and API secrets

One JSON is saved per run with model/provider, benchmark version, prompt/data/config hashes, anonymisation seed, tool trace, final structured decision, token usage, response IDs, latency and evaluation metrics. API credentials are never stored in records.

Credentials are read only from environment variables:

```bash
OPENAI_API_KEY
OPENAI_BASE_URL   # optional
OPENAI_MODEL
OPENAI_PROVIDER  # optional
```

`--provider auto` uses the Responses API where supported and can fall back to a compatible endpoint transport without changing the scientific task, tools or evaluator.
