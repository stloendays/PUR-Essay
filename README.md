# PUR-Essay

Data-driven polyurethane / HMPUR prepolymer rheology and formulation-decision research, with a blinded scientific-Agent benchmark layered on top of a deterministic science workflow.

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
  -> per-formulation rheology, Andrade fit    ln(eta) = A + B/T, Ea_app = R B
  -> rheological state (eta_ref, Ea)
  -> free-NCO / chemistry / temperature trends
  -> composition-context interaction
  -> candidate response landscape (PUR_SIM_V1, synthetic)
  -> nominal ranking -> feasibility -> minimax uncertainty/domain robustness   PUR-FRONTIER V1
  -> backward boundary -> reachability
  -> prospective wet-lab validation           data/prospective_validation/ (agent_access = false)
```

Code: `src/pur_science/` (objective, feasibility gates, frontier L0/L1/L2, backward threshold, reachability, local trends, Andrade).
Pre-freeze decision rule: `configs/frontier_v1.json`.

### B. Agent layer (PUR-RECOVER V1, never a source of truth)

```text
deterministic science -> freeze gold decision -> hide answer -> Agent receives admissible data
  -> Agent reasons / calls deterministic tools -> evaluator compares to frozen gold
```

Code: `src/pur_agent/`. The Agent can only read `benchmark/recover_v1/blind/` through a filesystem guard that refuses gold/evaluator/mapping/oracle/results/prospective paths.

## Decision frontier

```text
property optimum -> nominal feasible optimum -> minimax robust optimum
                 -> active constraint -> backward threshold -> reachable formulation
```

| Layer | Definition | Current status |
|---|---|---|
| L0 property-only | argmin `J = Σ log10(y/c)^2` over all 928 candidates | prior hypothesis `WO_INV_0419`; requires full response table to verify |
| L1 nominal constrained | same `J` after point-response broad/preferred windows, NCO:OH, MDI-fraction and chemistry-domain gates | historical ORACLE V2 winner `WO_INV_0579`; FRONTIER recomputation still requires full table |
| L2 robust | argmin `Σ (|log10(y/c)| + r)^2` over L1 candidates with `domain_ratio <= 1` | **not predetermined**; requires full response table |

FRONTIER V1 deliberately does **not** use full uncertainty-interval containment as a nominal or preferred-window hard gate. Complete-data responses define nominal feasibility; uncertainty is propagated afterwards through the same objective using a parameter-free worst-case/minimax score. Interval containment remains a diagnostic rather than a second certification task. See `docs/FRONTIER_V1.md`.

The earlier `WO_INV_0420` result is retained only as a prior robust hypothesis and, independently, as a verified backward-design point on the 50/50 PPG700/PPG1000 trajectory. It is **not** hard-coded as the robust gold.

Verified from the real design grid: for the 50/50 PPG700/PPG1000 blend,

```text
mdi_parts = 30.3875 * NCO:OH
```

so the 35 wt% MDI floor is crossed continuously at **NCO:OH = 1.7720**, and the first reachable 0.1-grid point is **1.8** (`WO_INV_0420`). `WO_INV_0419` at NCO:OH 1.7 has about 34.06 wt% MDI and fails this boundary.

## Data status — current blocker

The complete `PUR_SIM_V1` response table (928 rows with eta80, eta120, ratio, uncertainty radius and domain descriptors) is **not in this repository**. See `docs/PROJECT_STATE_AUDIT.md` and `data/pur_sim_v1/README.md`.

Available:

- `data/pur_sim_v1/design_space_928.csv` — real 928-row formulation/design grid;
- `data/oracle_top30_compact.csv` — historical 10-row feasible ranked snapshot;
- `results/oracle_v2/oracle_best.json` — frozen historical L1 result.

The old v0.7 response table comes from a different model and is not substituted. No response values are reconstructed or fabricated to fill the gap.

Restore the exact original response table as:

```text
data/pur_sim_v1/candidates_full.csv
```

then run:

```bash
python scripts/freeze_frontier_v1.py
```

The freeze script refuses partial input by default, records data/config hashes, computes L0/L1/L2, and reports any disagreement with prior hypotheses without modifying the data.

## Quick start

```bash
git pull
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -e ".[agent,dev]"
pytest

# 1. Restore the exact full PUR_SIM_V1 table, then freeze the deterministic frontier
python scripts/freeze_frontier_v1.py

# 2. Build anonymised blind bundle + evaluator-only gold and verify isolation
python scripts/build_blind_bundle.py
python scripts/verify_no_leakage.py

# 3. Dry run without API key
python scripts/run_agent_once.py --provider mock --condition pur_agent

# 4. Real API runs — secrets only through environment variables
export OPENAI_API_KEY="..."
export OPENAI_BASE_URL=""       # optional
export OPENAI_MODEL="..."
python scripts/run_agent_once.py
python scripts/run_agent_benchmark.py --runs 20
python scripts/run_baselines.py --runs 20
python scripts/summarize_benchmark.py
```

`--provider auto` uses the OpenAI Responses API and falls back to Chat Completions for compatible providers that do not expose Responses. Prompts, deterministic tools and evaluator remain fixed.

Secondary named-chemistry benchmark:

```bash
python scripts/build_blind_bundle.py --no-anonymize --blind-dir benchmark/recover_v1_named/blind --evaluator-dir benchmark/recover_v1_named/evaluator_only
```

## Benchmark conditions and metrics

Conditions (`src/pur_agent/conditions.py`): deterministic oracle, direct LLM, tool-using LLM, full PUR-Agent, and planned ablations.

Primary metric: **complete_decision_recovery**. A run must recover the decision chain, not merely guess a winner. Component metrics include top-1/3/5 recovery, oracle rank, objective regret, hard-constraint violations, backward-threshold error, reachability accuracy, explanation fidelity, tool calls, token usage, API calls and latency.

## Repository map

| Path | Role |
|---|---|
| `docs/PROJECT_STATE_AUDIT.md` | project/version/data-gap audit |
| `docs/RHEOLOGY_SCIENCE_V1.md`, `docs/NON_AGENT_WORKFLOW_V3.md` | active experimental/public science layer |
| `docs/FRONTIER_V1.md`, `configs/frontier_v1.json`, `src/pur_science/` | pre-freeze deterministic frontier rule and implementation |
| `docs/AGENT_STRATEGY_V1.md`, `configs/recover_v1.json`, `src/pur_agent/` | blinded Agent strategy |
| `docs/WORKFLOW_V2.md`, `docs/PAPER_MODEL_V2.md`, `configs/oracle_v2.json`, `results/oracle_v2/` | frozen historical PUR-ORACLE V2 provenance |
| `data/pur_sim_v1/` | design grid and location for restored full response table |
| `results/frontier_v1/` | generated only after complete-table freeze |
| `benchmark/`, `gold/`, `results/recover_v1/` | blind benchmark, evaluator-only gold and Agent outputs |
| `figures/`, `data/figures/` | manuscript Figures 2–4 and their source data |
| `manuscript/` | versioned paper drafts |

## Claim boundary

Experimental/public evidence supports the physical rheology conclusions: formulation-specific temperature sensitivity, free-NCO trends, temperature-amplified chemistry contrast and composition-context effects.

`PUR_SIM_V1` is a synthetic decision benchmark. It supports finite-space optimisation, constraint propagation, interval robustness, backward calculation and blind Agent recovery only. Synthetic candidate responses are not described as experimentally discovered physical laws, and prospective wet-lab results never enter the primary blind Agent benchmark.
