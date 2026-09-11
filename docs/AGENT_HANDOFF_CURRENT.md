# Current Agent handoff — PUR-RECOVER V1 / V2 design transition

**Status:** real-API pilot completed; frozen science remains V1, Agent orchestration is being upgraded under `docs/AGENT_WORKFLOW_V2.md`.

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

For the V2 formal matrix, add separately versioned conditions such as:

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

## Immediate next steps

1. Read `docs/AGENT_WORKFLOW_V2.md` and inspect the current `src/pur_agent/strategy.py`, `runtime.py`, `tools.py`, `audit_tools.py`, `schemas.py`, and evaluator code.
2. Implement V2 as an additive/versioned path; keep existing V1/pilot paths runnable.
3. Normalize the `mdi_fraction` / `mdi_fraction_min` naming inconsistency through one canonical constraint object before formal V2 runs, and apply it consistently to all V2 conditions.
4. Add deterministic decision-certificate generation and dual-path threshold verification.
5. Add V2 unit/integration/leakage tests.
6. Run mock smoke tests first, then a small real-API pilot.
7. Freeze a new V2 run manifest before the 30–50-run formal matrix.
8. Preserve all negative and transport/schema failure records.

Do not modify the wet-lab plan or frozen science merely to improve Agent benchmark performance.