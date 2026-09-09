# PUR-RECOVER V1 Agent strategy

## Design principle

The Agent is a **blinded scientific decision-recovery system**, not an optimizer that owns the answer. The
deterministic science layer (PUR-FRONTIER V1) freezes the rules and the gold decision first; the Agent is
evaluated afterwards.

```text
Deterministic science -> freeze gold -> hide answer -> Agent gets admissible data
  -> Agent reasons / uses tools -> Evaluator compares Agent result to frozen gold
```

## What the Agent sees / does not see

Sees (inside `benchmark/recover_v1/blind/` only): anonymised candidate table (all rows, all descriptors,
responses, domain ratio, uncertainty radius, in-domain flag), the public benchmark config (objective, hard
constraints, robustness definition, backward and local-trend definitions), the task statement with a provenance
block, and the deterministic tools.

Never sees: gold IDs, oracle ranks/scores/best flags, ordered ranking lists, mapping files, evaluator files,
`results/`, `data/prospective_validation/`, wet-lab results. Enforced by `pur_agent.data_access.BundleReader`
(filesystem guard), `scripts/verify_no_leakage.py` (content scan + guard self-test) and `tests/test_no_gold_leakage.py`.

## Strategy stack

1. **Anonymisation** — deterministic, seed-fixed mapping of candidate IDs (`Candidate_0001…`) and polyols
   (`Polyol_A…`); mapping stored evaluator-side only. A secondary named-chemistry benchmark tests domain priors.
2. **Deterministic tool grounding** — ranking, feasibility, backward solving, reachability and sweeps are Python
   tools delegating to `pur_science`; the LLM plans, selects tools and reasons.
3. **Complete-decision recovery** — property winner, constrained winner, robust winner (or explicit abstention),
   active constraint, backward threshold, reachable grid value, reachability verdict, NCO direction, composition
   direction (with the axis named). A lucky winner guess is not a success.
4. **Trace gating** — `RecoveryStrategy` records required tool families. In the full Agent a final answer is
   rejected (up to three corrective turns) until the deterministic chain has been inspected. Tools removed by an
   ablation are not required, so ablated Agents can finish and are scored on what they could not recover.
5. **Robustness abstention** — if the robust layer is not frozen, `rank_robust` fails deterministically and the
   Agent must set `robust_winner = null` with a reason.
6. **Independent evaluation** — `complete_decision_recovery` is primary; component metrics are diagnostic.
7. **Wet-lab separation** — prospective measurements are excluded from the primary benchmark.

## Conditions

| Condition | Tools | Strategy guard | Prompt | Notes |
|---|---|---|---|---|
| `oracle` | — | — | — | Baseline 0, deterministic frontier on the blind table |
| `direct_llm` | none | no | `direct_llm_system.txt` | compressed full table in context |
| `tool_llm` | all | no | `tool_llm_system.txt` | tools without planning/enforcement |
| `pur_agent` | all | yes | `recover_v1_system.txt` | plan → inspect → constrain → calculate → backward → self-check → final |
| `pur_agent_no_backward` | minus backward/reachability | yes | same | ablation |
| `pur_agent_no_constraint_checker` | minus constraint audit / constrained & robust ranking | yes | same | ablation |
| `pur_agent_no_provenance` | all | yes | same, no provenance block | ablation |
| `pur_agent_single_pass` | all | no | same | ablation |

Negative results are kept as they are; no condition is tuned after seeing results.

## Output schema

```json
{
  "property_winner": "Candidate_XXXX",
  "constrained_winner": "Candidate_XXXX",
  "robust_winner": "Candidate_XXXX or null",
  "robust_abstention_reason": "string or null",
  "active_constraint": {"name": "...", "threshold": 0.0, "candidate_value": 0.0, "evidence": "..."},
  "backward_design": {"variable": "nco_oh", "continuous_threshold": 0.0, "nearest_reachable_grid_value": 0.0, "reachable": true, "active_constraint": "..."},
  "local_trends": {"nco_direction": "...", "composition_axis": "...", "composition_direction": "...", "notes": "..."},
  "evidence": [], "final_reasoning_summary": "...", "confidence": 0.0, "abstain": false, "abstention_reason": null
}
```

## Run records

One JSON per run with: run_id, timestamp, benchmark id, condition, provider, model, prompt/data/config SHA256,
anonymisation seed, LLM seed, tool trace (name, arguments, output), final JSON, raw text, token usage, API
response ids, latency, strategy check, evaluation metrics. Records are scrubbed of anything that looks like an
API key.

## Providers

`OPENAI_API_KEY`, optional `OPENAI_BASE_URL`, `OPENAI_MODEL` from the environment only. `--provider auto`
uses the Responses API and falls back to Chat Completions when a compatible provider does not serve it. The
scientific task, prompts, tools and evaluator do not change with the transport. `--provider mock` runs the whole
pipeline offline (the mock follows the tool strategy literally with tools, and abstains without tools).
