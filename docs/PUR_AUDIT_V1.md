# PUR-AUDIT V1 — secondary blinded decision-audit mode

Status: implemented (tools, gold, scorer, mock, condition `pur_audit`); no real-API runs yet.
It does **not** change the PUR-RECOVER V1 primary benchmark: same blind bundle, same frozen
`configs/frontier_v1.json` contract, same anonymisation, same filesystem guard. Only the task,
the tool set and the scorer differ. Config: `configs/audit_v1.json`.

## Question

PUR-RECOVER V1 asks "can the Agent recover the frozen decision chain?". PUR-AUDIT V1 asks
"can the Agent explain the decision and its fragility, and report contradictions instead of
forcing an answer?".

## What the auditor must deliver

| Block | Content | Deterministic source |
|---|---|---|
| `layer_divergence` | why L0 ≠ L1 (active constraint), why L1 ≠ L2 (`worst_case_objective` vs `robust_admissibility_gate`), which response is the robust winner's broad-window bottleneck | `constraint_audit`, `uncertainty_counterfactual`, `score_crossover` |
| `constraint_counterfactual` | how far the frozen MDI floor can rise or fall before the robust winner changes, and to whom | `constraint_counterfactual` (phase map over the floor) |
| `uncertainty_counterfactual` | uncertainty scale at which L1 and L2 winners cross; scale range over which the robust winner is stable | `uncertainty_counterfactual`, `score_crossover` |
| `reachability` | is the property-only target reachable on the grid; nearest reachable NCO:OH | `solve_backward_threshold`, `check_reachability` |
| `objective_structure` | does the frozen objective double-count (eta80 = eta120 × ratio); principal weight ratio of the induced metric | `objective_structure_audit` |
| `pareto_alternatives` | non-dominated robust-admissible candidates (|log d| per response, radius, domain ratio) | `pareto_alternatives` |
| `stability` | weight-fraction of the nominal and robust winners under Dirichlet-random objective weights; verdict | `weight_stability` |
| `hypothesis_to_test` | one hypothesis most worth a wet-lab test, with the tool outputs that motivate it | free text, must cite tools |
| `contradictions` | any inconsistency between tool outputs or with the frozen chain | `consistency_report` |

The LLM cannot modify the objective, constraints, uncertainty rule or gold: every audit tool is
a wrapper over `pur_science.depth`, which only reads the frozen frontier table and config.
`objective_structure_audit` reports the double-counting; it never proposes or applies a fix,
because a corrected objective would be a new benchmark version.

## Frozen audit gold (evaluator-only, `gold_audit.json`)

Computed by `pur_agent.audit.audit_gold` from the same functions. On the recovered 928 table:

```text
L0 -> L1 reason              mdi_fraction
L1 -> L2 mechanism           worst_case_objective   (WO_INV_0579 is robust-admissible; it loses on worst-case score)
bottleneck response of L2    ratio
MDI floor stability of L2    [0.345868, 0.353577]  (raise by 0.0036 -> winner changes; lower by 0.0041 -> changes)
L1/L2 crossover scale        0.3637  (below this uncertainty scale the constrained winner would also be robust winner)
objective double-counting    true, principal weight ratio 3.0
nominal winner weight-frac.  0.798   robust winner weight-frac. 0.442  -> robust decision is weight-fragile
contradictions               none
```

These are decision-geometry properties of synthetic PUR_SIM_V1, reproduced exactly by
`tests/test_depth.py` against the frozen `results/frontier_depth_v1/` outputs.

## Scoring (`pur_agent.audit.score_audit`)

Per-field recovery with declared tolerances (floor 0.002, scale 0.02, weight fraction 0.05,
Pareto Jaccard ≥ 0.6 and must contain the robust winner, principal ratio ±0.1), plus
`hypothesis_present` (non-empty statement citing at least one tool), `false_contradictions`
(reported but not in gold), `missed_contradictions`. Primary metric: `audit_completeness` =
every deterministic field recovered, no false or missed contradictions, no abstention.
The scientific merit of the hypothesis is not machine-scored; it is left to human review.

## Strategy gate

`AuditStrategy` requires the recovery chain (audit, property/constrained/robust ranking,
constraint audit, backward, reachability) plus every counterfactual family
(constraint, uncertainty, objective structure, Pareto, stability, consistency) before the
model may finalize. Local sweeps are not required in audit mode.

## Running

```bash
python scripts/build_blind_bundle.py --config configs/audit_v1.json --blind-dir benchmark/audit_v1/blind --evaluator-dir benchmark/audit_v1/evaluator_only --gold-dir gold/audit_v1
python scripts/verify_no_leakage.py --blind-dir benchmark/audit_v1/blind --evaluator-dir benchmark/audit_v1/evaluator_only --config configs/audit_v1.json
python scripts/run_agent_once.py --provider mock --condition pur_audit --blind-dir benchmark/audit_v1/blind
python scripts/run_agent_benchmark.py --condition pur_audit --runs 5 --blind-dir benchmark/audit_v1/blind
```

The primary `benchmark/recover_v1/` bundle also carries `gold_audit.json`, so `pur_audit` can
be run on it directly; the separate `audit_v1` bundle only differs in `benchmark_id` and task text.

## Claim boundary

All audit quantities are algorithmic properties of the frozen synthetic space. They say how
fragile the frozen computational decision is; they do not say anything about physical
polyurethane behaviour, which only the prospective experiment can test.
