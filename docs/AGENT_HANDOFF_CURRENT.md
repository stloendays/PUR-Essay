# Current Agent handoff — PUR-RECOVER V1 / V2 design transition

**Status (2026-09-11):** the V1 real-API pilot is complete and preserved. V2 orchestration is now **implemented** (see `docs/AGENT_WORKFLOW_V2.md` §16) and green under mock: `pytest -q` 129 passed, both blind bundles rebuilt, both leakage scans PASS. The real-API V2 pilot has **not** run — the configured endpoint `http://127.0.0.1:8788/v1` refuses connections — so there is no V2 API evidence yet and no claim of V2 superiority. Frozen science is unchanged.

## Read this before touching Agent code

The paper no longer uses an Agent to select experiments, maximize information gain, or define the scientific optimum. The deterministic science layer is frozen first. The Agent is then tested on whether it can recover the already-frozen decision chain while the answer is hidden.

```text
real/source-grounded rheology
  -> deterministic PUR-FRONTIER V1
  -> freeze gold
  -> build anonymised blind bundle
  -> PUR-RECOVER Agent / baselines / ablations
  -> evaluator-only comparison with frozen gold
  -> prospective wet-lab validation remains separate
```

The first real-API pilot is already preserved under `results/recover_v1/pilot_20260910_b/` (commit `9dc5ae2`). It showed that deterministic tool grounding clearly improves over direct LLM reasoning, while `tool_llm` and the current `pur_agent` were indistinguishable at n=3. Therefore the next Agent phase must test a genuinely more distinctive orchestration layer rather than adding decorative complexity.

## Canonical current Agent code

Use these paths:

- `src/pur_agent/`
- `src/pur_science/`
- `configs/frontier_v1.json`
- `configs/recover_v1.json`
- `docs/AGENT_STRATEGY_V1.md`
- `docs/AGENT_WORKFLOW_V2.md`  **<- post-pilot orchestration upgrade spec**
- `docs/FRONTIER_V1.md`
- `docs/FRONTIER_DEPTH_V1.md`
- `docs/PUR_SIM_V1_RECOVERY_AUDIT.md`
- `prompts/recover_v1_system.txt`
- `prompts/recover_v1_task.txt`
- `prompts/direct_llm_system.txt`
- `prompts/tool_llm_system.txt`
- `scripts/build_blind_bundle.py`
- `scripts/run_agent_once.py`
- `scripts/run_agent_benchmark.py`
- `scripts/run_baselines.py`
- `scripts/evaluate_agent_runs.py`
- `scripts/summarize_benchmark.py`
- `scripts/verify_no_leakage.py`
- `tests/test_recover_v1.py`
- `tests/test_no_gold_leakage.py`

### Historical code that is NOT the current paper Agent

Do not extend the current paper from `src/pur_bridge/agent.py`.

That module belongs to the historical E6 / active-learning / information-gain pathway and contains concepts such as:

- `E6_star`;
- experiment selection;
- information gain;
- material-equivalence gating as the primary Agent action;
- post-E6 adaptive decisions.

It is retained for provenance/legacy compatibility only. It is not PUR-RECOVER.

## Frozen scientific contract

The Agent is a **blinded scientific decision-recovery system**, not an optimizer that owns the answer.

Evaluator-side frozen decision chain:

```text
L0 property winner      WO_INV_0419
L1 constrained winner   WO_INV_0579
L2 robust winner        WO_INV_0420
active boundary         MDI fraction >= 0.35
continuous threshold    NCO:OH = 1.7719836724
first reachable grid    NCO:OH = 1.8
```

These source IDs and evaluator-only outputs must never be placed in the primary Agent prompt or blind candidate table.

The primary Agent may receive only the generated contents of `benchmark/recover_v1/blind/` plus approved prompts/tools. It must not read evaluator mapping/gold, source IDs, stored oracle ranks/scores, ordered gold rankings, `results/frontier_v1/`, `results/frontier_depth_v1/`, `data/prospective_validation/`, or manuscript passages that explicitly reveal the gold decision during a primary blind run.

## Primary task

A complete successful run must recover, in anonymised candidate labels:

1. L0 property winner;
2. L1 nominal constrained winner;
3. L2 robust winner;
4. active constraint;
5. continuous backward threshold;
6. nearest reachable grid point and reachability verdict;
7. local NCO direction;
8. local composition direction.

A lucky top-1 guess is not complete success. The primary metric remains `complete_decision_recovery`.

## Post-pilot V2 orchestration target

The frozen science above does not change. Only the way the Agent reaches, challenges, certifies, and explains the same answer is upgraded.

```text
PLAN -> SOLVE -> CHALLENGE -> CERTIFY -> EXPLAIN
```

Required V2 features are specified in `docs/AGENT_WORKFLOW_V2.md`:

- claim-level minimum-sufficient evidence planning;
- deterministic numerical solve;
- counterfactual scientific challenge before finalization;
- dual-path verification for critical quantities such as the backward threshold;
- canonical constraint ontology (`quantity`, `operator`, `threshold`);
- deterministic machine-auditable decision certificate;
- structured conflict/abstention when tools disagree;
- continued strict separation from prospective wet-lab data.

Do **not** assume V2 is superior. Implement it as a separate benchmark condition/version and test it against `tool_llm` and current V1-style baselines.

## Benchmark conditions to preserve

Existing pilot conditions remain immutable evidence:

- `oracle`;
- `direct_llm`;
- `tool_llm`;
- `pur_agent`;
- `pur_agent_no_backward`;
- `pur_agent_no_constraint_checker`;
- `pur_agent_no_provenance`;
- `pur_agent_single_pass`.

For the V2 formal matrix, these separately versioned conditions are now registered:

- `pur_agent_v2`;
- `pur_agent_v2_no_evidence_planner`;
- `pur_agent_v2_no_challenge`;
- `pur_agent_v2_no_cross_path`;
- `pur_agent_v2_no_certificate`.

Do not overwrite or reinterpret the existing pilot records.

## Wet-lab rule

The PPG2000 / STEPANPOL PDP-70 / 4,4'-MDI five-point experiment has already started. Do not redesign it to fit the Agent.

Before any experimental result is used to modify Agent logic, freeze only genuinely pre-result predictions and falsification criteria. If any result has already been inspected, record the timing truthfully and do not retroactively call a prediction preregistered. Wet-lab measurements remain excluded from the primary PUR-RECOVER Agent input.

## API and secret handling

The repository must never contain a real API credential. Read credentials only from environment variables:

```text
OPENAI_API_KEY
OPENAI_BASE_URL
OPENAI_MODEL
OPENAI_PROVIDER
```

Do not print keys to logs or save them in run JSON. `.env` and local secret files remain ignored.

## What may be changed now

It is acceptable to change:

- Agent orchestration and policy;
- claim-evidence planning structures;
- challenge/counterfactual wrappers that reuse frozen science;
- cross-path consistency checks;
- canonical ontology helpers;
- deterministic certificate generation;
- JSON schema extensions, logging, metrics and V2 evaluator diagnostics;
- benchmark orchestration and tests.

Do not change:

- `PUR_SIM_V1` responses;
- `configs/frontier_v1.json` objective/constraints;
- L0/L1/L2 definition;
- robust uncertainty rule;
- backward threshold definition;
- evaluator tolerances to rescue a model;
- anonymisation to leak chemistry identities;
- wet-lab results into the primary Agent input.

If a scientific-contract bug is independently demonstrated, version the benchmark and rerun all affected conditions rather than silently patching the current task.

## V2 artefacts

The V2 benchmark is versioned separately and shares the blind candidate table byte-for-byte with V1 (`blind_candidate_sha256 = 6ca33d4e…`), so the two are directly comparable:

- config: `configs/recover_v2.json` (science still inherited from `configs/frontier_v1.json`);
- bundle: `benchmark/recover_v2/blind/`, gold: `benchmark/recover_v2/evaluator_only/` and `gold/recover_v2/`;
- prompts: `prompts/recover_v2_system.txt`, `prompts/recover_v2_task.txt`;
- code: `ontology.py`, `evidence.py`, `challenge_tools.py`, `crosspath.py`, `certificate.py`, `tools_v2.py`, `mock_llm_v2.py`;
- tests: `tests/test_agent_v2.py`;
- manifest freezer: `scripts/freeze_run_manifest.py`.

The V2 gold's scientific fields are identical to V1's; only `benchmark_id`, `config_sha256` and `frozen_utc` differ.

## Immediate next steps

1. Start the local model endpoint (`http://127.0.0.1:8788/v1`) and confirm it answers before spending runs.
2. Run the small real-API V2 pilot (commands in `docs/PILOT_RUNBOOK.md`), keeping every failed, invalid and transport-error record.
3. Compare `tool_llm` against `pur_agent_v2` on the primary metric **and** on the V2 diagnostics, reporting `first_answer_gate_clean_rate` alongside `schema_correctness_rate` so the gate's own contribution is visible.
4. Freeze the run manifest with `scripts/freeze_run_manifest.py` on a clean worktree before the 30–50-run formal matrix.
5. If `tool_llm` and `pur_agent_v2` stay indistinguishable, report that negative result rather than retuning anything.

Do not modify the wet-lab plan or frozen science merely to improve Agent benchmark performance.