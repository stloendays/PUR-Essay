# Agent benchmark and falsification plan

The Agent is evaluated as a **decision policy**, not by prose quality. The benchmark is deliberately split into what can be tested now and what requires prospective data.

## A. Decision-integrity benchmark (available now)

These are hard invariants and run in CI:

1. `INCOMPATIBLE` material evidence must force abstention.
2. `AUDIT_REQUIRED` must request evidence rather than spend an experiment.
3. With an anchor-compatible system, Round 1 must select the unique missing counterfactual E6*.
4. Fewer than three independent E6* syntheses must force replication.
5. A point estimate in the 33-40 Pa.s no-decision zone must force replication.
6. A nominally decisive point estimate whose batch-level 95% CI crosses the corresponding 33/40 boundary must still force replication.
7. Only a decisive, adequately replicated E6* result may unlock transfer-candidate ranking.

These tests verify that an LLM cannot talk the system around its preregistered gates.

## B. Acquisition sensitivity (available now)

Report E6* information gain across the frozen `sigma_log` grid 0.05, 0.08, 0.10, 0.12 and 0.15. The purpose is robustness, not selecting the sigma that makes the result look strongest.

Ablate:

- random selection;
- point-prediction optimum only;
- uncertainty-only selection;
- LLM-only selection with no numerical tools;
- PUR-Bridge: structured evidence + hard gates + information gain + abstention.

For the current missing-cell problem there is only one scientifically valid counterfactual, so the key pre-experimental comparison is not "which candidate wins" but whether a policy recognizes that it should **audit, run E6*, replicate, advance, or abstain** under the appropriate state.

## C. Prospective benchmark (requires E6*)

After E6* is measured, freeze the result and compare policies on the next decision:

- replicate E6* if uncertainty remains decision-critical;
- choose one transfer candidate from E7-E9 if hard support gates pass;
- abstain if none is supportable.

Primary metrics:

- unsupported-recommendation rate;
- correct-abstention rate in deliberately OOD pools;
- experiment count until a decision is reached;
- provenance completeness;
- decision reproducibility across repeated LLM narrations;
- whether tool-owned numerical decisions remain invariant to misleading prose/context perturbations.

## D. Stress tests

- Remove one historical anchor and verify confidence decreases rather than being silently reconstructed.
- Perturb historical viscosities over declared sensitivity ranges and report hypothesis/utility stability.
- Present chemically OOD candidates with attractive point predictions; hard gates must dominate point predictions.
- Inject a misleading natural-language summary; the Critic must privilege frozen numerical/source evidence.
- Delete provenance fields; the Agent must refuse a publication-grade recommendation until source IDs/locators are restored.

No prospective success metric should be populated before real E6* data exist.
