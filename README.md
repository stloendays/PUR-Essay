# PUR-Essay

Data-driven polyurethane / HMPUR prepolymer rheology and formulation decision research, with a
blinded scientific-Agent benchmark layered on top of a deterministic science workflow.

```text
The Agent is not the scientist that defines the answer.
The deterministic scientific workflow defines and freezes the answer.
The Agent is a blinded decision-recovery system evaluated against that answer.
The wet-lab experiment independently evaluates whether the frozen computational decision transfers to reality.
```

## Two strictly separated parts

### A. Non-Agent scientific layer (owns all scientific truth)

```text
heterogeneous experimental/public evidence
  -> source + protocol harmonization          docs/RHEOLOGY_SCIENCE_V1.md
  -> per-formulation rheology, Andrade fit     ln(eta) = A + B/T,  Ea_app = R B
  -> rheological state (eta_ref, Ea)
  -> free-NCO / chemistry / temperature trends
  -> composition-context interaction
  -> candidate response landscape (PUR_SIM_V1, synthetic)
  -> nominal ranking -> feasibility -> uncertainty/domain robustness   PUR-FRONTIER V1
  -> decision-frontier ranking -> backward boundary -> reachability
  -> prospective wet-lab validation           data/prospective_validation/ (agent_access = false)
```

Code: `src/pur_science/` (objective, feasibility gates, frontier L0/L1/L2, backward threshold,
reachability, local trends, Andrade). Frozen definitions: `configs/frontier_v1.json`.

### B. Agent layer (PUR-RECOVER V1, never a source of truth)

```text
deterministic science -> freeze gold decision -> hide answer -> Agent receives admissible data
  -> Agent reasons / calls deterministic tools -> evaluator compares to frozen gold
```

Code: `src/pur_agent/`. The Agent can only read `benchmark/recover_v1/blind/` through a
filesystem guard that refuses every gold/evaluator/mapping/oracle/results/prospective path.

## Decision frontier (what the paper reports)

```text
property optimum  ->  active formulation constraint  ->  backward threshold
                  ->  reachable discrete formulation ->  final robust decision
```

| Layer | Definition | Frozen ID (ORACLE V2 / documented FRONTIER expectation) |
|---|---|---|
| L0 property-only | argmin `J = Σ log10(y/c)^2` over all 928 candidates | documented `WO_INV_0419` (PPG700/PPG1000 50/50, NCO:OH 1.7) — **needs the full table to verify** |
| L1 nominal constrained | L0 objective under every ORACLE V2 hard gate | `WO_INV_0579` (frozen, `results/oracle_v2/oracle_best.json`) |
| L2 robust | worst-case of `J` over the frozen log10 interval, among candidates whose whole interval stays inside the preferred window and whose domain ratio <= 1 | documented `WO_INV_0420` (50/50, NCO:OH 1.8) — **needs the full table to verify** |

Verified locally from the real design grid: for the 50/50 PPG700/PPG1000 blend `mdi_parts = 30.3875 × NCO:OH`,
so the 35 wt% MDI floor is crossed at NCO:OH = **1.7720** (continuous) and the first reachable grid point is **1.8**.
`WO_INV_0419` (NCO 1.7, 34.06 wt%) is infeasible; `WO_INV_0420` is the first admissible point on that trajectory.

## Status of the data (read this first)

The complete `PUR_SIM_V1` response table (928 rows) that produced ORACLE V2 is **not in this repository**
(see `docs/PROJECT_STATE_AUDIT.md` §10 and `data/pur_sim_v1/README.md`). Only the real design grid
(`data/pur_sim_v1/design_space_928.csv`) and a 10-row ranked snapshot (`data/oracle_top30_compact.csv`) are
present. Nothing was synthesised to fill the gap. Place the full table at
`data/pur_sim_v1/candidates_full.csv` to freeze the frontier and build the blind benchmark.

## Quick start

```bash
git pull
python -m venv .venv            # or use an existing environment
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -e ".[agent,dev]"
pytest                          # deterministic tests, no API key needed

# 1. freeze the deterministic frontier (requires the full PUR_SIM_V1 table)
python scripts/freeze_frontier_v1.py            # -> results/frontier_v1/

# 2. build the anonymised blind bundle + evaluator-only gold, then prove isolation
python scripts/build_blind_bundle.py            # -> benchmark/recover_v1/{blind,evaluator_only}, gold/recover_v1
python scripts/verify_no_leakage.py             # must print PASS

# 3. dry run without any API key
python scripts/run_agent_once.py --provider mock --condition pur_agent

# 4. real runs — keys only via environment variables (see .env.example)
export OPENAI_API_KEY="..."
export OPENAI_BASE_URL=""       # optional, OpenAI-compatible providers
export OPENAI_MODEL="..."
python scripts/run_agent_once.py                       # one PUR-Agent run, evaluated against gold
python scripts/run_agent_benchmark.py --runs 20        # repeated runs, summary.csv/json
python scripts/run_baselines.py --runs 20              # oracle, direct_llm, tool_llm, pur_agent + ablations
python scripts/summarize_benchmark.py                  # results/recover_v1/summary.{csv,json}
```

`--provider auto` (default) uses the OpenAI Responses API and falls back to Chat Completions for
providers that do not serve it; prompts, tools and evaluator are identical either way.
Secondary named-chemistry benchmark: `python scripts/build_blind_bundle.py --no-anonymize --blind-dir benchmark/recover_v1_named/blind --evaluator-dir benchmark/recover_v1_named/evaluator_only`.

## Benchmark conditions and metrics

Conditions (`src/pur_agent/conditions.py`): `oracle` (Baseline 0, deterministic), `direct_llm` (data in
context, no tools), `tool_llm` (tools, no strategy enforcement), `pur_agent` (plan -> inspect -> constrain ->
calculate -> backward -> self-check -> gated final answer), ablations `pur_agent_no_backward`,
`pur_agent_no_constraint_checker`, `pur_agent_no_provenance`, `pur_agent_single_pass`.

Metrics (`src/pur_agent/metrics.py`): top-1/3/5 recovery, oracle rank, objective regret, hard-constraint
violation rate, **complete_decision_recovery** (primary: all three winners + active constraint + backward
threshold within 0.03 NCO:OH + reachable grid value + reachability verdict + both local trend directions),
backward-threshold error, reachability accuracy, explanation fidelity, tool-call count, token usage, API calls,
latency. Every run is stored as `results/recover_v1/<condition>/<model>/runs/run_XXXX.json` with prompt, data
and config hashes, anonymisation seed, LLM seed, full tool trace, final JSON, response IDs and usage. API keys
are never written (records are scrubbed).

## Repository map

| Path | Role |
|---|---|
| `docs/PROJECT_STATE_AUDIT.md` | audit of versions, conflicts, leakage risks, data gap |
| `docs/RHEOLOGY_SCIENCE_V1.md`, `docs/NON_AGENT_WORKFLOW_V3.md` | active science layer |
| `docs/FRONTIER_V1.md` | frozen decision-frontier definition and backward-design method |
| `docs/AGENT_STRATEGY_V1.md` | Agent benchmark design |
| `docs/WORKFLOW_V2.md`, `docs/PAPER_MODEL_V2.md`, `docs/VALIDATION_EXPERIMENT_V2.md`, `configs/oracle_v2.json`, `results/oracle_v2/` | PUR-ORACLE V2 (frozen L1 benchmark) |
| `configs/frontier_v1.json`, `src/pur_science/`, `results/frontier_v1/` | PUR-FRONTIER V1 |
| `configs/recover_v1.json`, `src/pur_agent/`, `prompts/`, `benchmark/`, `gold/`, `results/recover_v1/` | PUR-RECOVER V1 |
| `src/pur_bridge/`, `configs/pur_bridge_v1.json`, `legacy/` | PUR-Bridge v0.7 / v1.1, frozen provenance |
| `figures/`, `data/figures/` | manuscript Figures 2–4 (R) |

## Claim boundary

Experimental/public evidence (Pugar library, US5932680A, WO2018173768) supports: temperature-dependent
rheology, formulation-specific Ea, free-NCO trends, temperature-amplified chemistry contrast and the
composition-context effect. The synthetic `PUR_SIM_V1` space supports only: algorithm benchmark, finite-space
optimisation, ranking propagation, constraint handling, backward calculation and blind Agent recovery. Synthetic
candidate responses are never described as an experimentally discovered physical law, and prospective wet-lab
results never enter the primary blind benchmark.
