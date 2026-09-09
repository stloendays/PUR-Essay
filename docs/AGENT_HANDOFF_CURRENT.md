# Current Agent handoff — PUR-RECOVER V1

**Status:** current paper Agent framework as of 2026-09-09.

## Read this before touching Agent code

The paper no longer uses an Agent to select experiments, maximize information gain, or define the scientific optimum. The deterministic science layer is frozen first. The Agent is then tested on whether it can recover the already-frozen decision chain while the answer is hidden.

```text
real/source-grounded rheology
  -> deterministic PUR-FRONTIER V1
  -> freeze gold
  -> build anonymised blind bundle
  -> PUR-RECOVER V1 Agent / baselines / ablations
  -> evaluator-only comparison with frozen gold
  -> prospective wet-lab validation remains separate
```

### Canonical current Agent code

Use these paths:

- `src/pur_agent/`
- `src/pur_science/`
- `configs/frontier_v1.json`
- `configs/recover_v1.json`
- `docs/AGENT_STRATEGY_V1.md`
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

It is retained for provenance/legacy compatibility only. It is not PUR-RECOVER V1.

## Scientific contract

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

The primary Agent may receive only the generated contents of `benchmark/recover_v1/blind/` plus the approved current prompts/tools. It must not read:

- evaluator mapping files;
- evaluator gold decisions;
- source candidate IDs;
- stored oracle ranks/scores/best flags;
- ordered gold ranking lists;
- `results/frontier_v1/` during a primary blind run;
- `results/frontier_depth_v1/` during a primary blind run;
- `data/prospective_validation/`;
- manuscript passages that explicitly reveal the gold decision.

Developer-side code may know where evaluator files live, but the **model-under-test context and tool filesystem must remain isolated** from them.

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

A lucky top-1 guess is not complete success.

The primary metric is `complete_decision_recovery`. Diagnostics include Top-1/3/5, recovered rank, objective regret, constraint violations, backward-threshold error, reachability accuracy, explanation fidelity, tool calls, API calls, token usage and latency.

## Conditions to preserve

Formal benchmark conditions are:

- `oracle` — deterministic reference, not an Agent competitor;
- `direct_llm` — language-only baseline;
- `tool_llm` — deterministic tools without full strategy enforcement;
- `pur_agent` — full current strategy;
- `pur_agent_no_backward` — backward/reachability ablation;
- `pur_agent_no_constraint_checker` — constraint/ranking ablation;
- `pur_agent_no_provenance` — provenance ablation;
- `pur_agent_single_pass` — planning/trace-enforcement ablation.

Do not retune a condition after formal benchmark results are visible. Negative results are retained.

## Required execution order

```bash
git pull origin main
python -m venv .venv
# Linux/macOS:
. .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1

pip install -e ".[agent,dev]"
pytest -q

# Reconstruct and verify the frozen science first.
python scripts/freeze_frontier_v1.py

# Build primary anonymised blind bundle and evaluator-only gold.
python scripts/build_blind_bundle.py
python scripts/verify_no_leakage.py

# Infrastructure smoke only — not publishable model performance.
python scripts/run_agent_once.py --provider mock --condition pur_agent
python scripts/run_baselines.py --runs 2 --provider mock

# Only after all tests/leakage checks pass: real API pilot.
# Credentials must be environment variables and must never be committed.
# OPENAI_API_KEY=...
# OPENAI_BASE_URL=...   # optional OpenAI-compatible endpoint
# OPENAI_MODEL=...

python scripts/run_agent_benchmark.py --condition pur_agent --runs 5
python scripts/run_baselines.py --conditions direct_llm tool_llm pur_agent --runs 5
```

After the pilot is stable, freeze prompts/config/code hashes and start formal repeated runs. Recommended manuscript target is 30–50 independent runs per LLM condition/configuration if API cost permits. Use a fixed declared seed schedule; do not discard failed runs, invalid JSON runs, timeouts or scientifically incorrect runs.

Then evaluate and aggregate:

```bash
python scripts/evaluate_agent_runs.py results/recover_v1
python scripts/summarize_benchmark.py
```

## API and secret handling

The repository must never contain a real API credential. Read credentials only from environment variables:

```text
OPENAI_API_KEY
OPENAI_BASE_URL   # optional
OPENAI_MODEL
OPENAI_PROVIDER   # optional
```

Do not print the key to logs or save it in run JSON. `.env`/local secret files must remain ignored.

## What may be changed now

It is acceptable to fix:

- provider/API transport;
- tool-call plumbing;
- retry/error recording;
- JSON schema enforcement;
- deterministic tool wrappers;
- run logging and usage capture;
- blind-bundle isolation/leakage checks;
- benchmark orchestration;
- aggregation and Figure 7-ready result tables.

Do **not** change after inspecting gold/performance:

- `PUR_SIM_V1` responses;
- `configs/frontier_v1.json` scientific objective/constraints;
- L0/L1/L2 definition;
- robust uncertainty rule;
- backward threshold definition;
- evaluator tolerances to rescue a model;
- anonymisation to leak chemistry identities into the primary benchmark;
- wet-lab results into the Agent input.

If a scientific-contract bug is discovered, stop formal runs, document the bug, version a new benchmark, and rerun all conditions from scratch rather than silently patching the frozen task.

## Deliverables for the next Agent phase

The Agent implementation phase is complete only when the repository contains:

1. passing unit/integration/leakage tests;
2. reproducible blind-bundle manifest and hashes;
3. real-API pilot records;
4. formal repeated run records for all declared conditions;
5. summary CSV/JSON with complete-decision recovery and diagnostics;
6. a failure taxonomy (ranking, constraint, backward, reachability, schema/API);
7. token/API/latency accounting;
8. Figure 7-ready data, but no fabricated or mock performance;
9. a concise runbook listing the exact commands, model IDs, API/provider versions, prompt/config/data hashes and seed schedule.

Wet-lab validation is a separate later layer and must not be used to tune PUR-RECOVER V1.