# PUR-Essay

Data-driven polyurethane / HMPUR prepolymer rheology and formulation-decision research, with a blinded scientific-Agent benchmark layered on top of a deterministic science workflow.

```text
The deterministic scientific workflow defines and freezes the answer.
The Agent is a blinded decision-recovery system evaluated against that answer.
The wet-lab experiment independently evaluates whether the frozen computational decision transfers to reality.
```

## Scientific workflow

```text
experimental/public evidence
  -> source + protocol harmonization
  -> formulation-specific Andrade rheology (eta_ref, Ea)
  -> free-NCO / chemistry / temperature trends
  -> composition-context interaction
  -> PUR_SIM_V1 finite candidate landscape
  -> L0 property ranking
  -> L1 nominal chemistry/process feasibility
  -> L2 interval/domain robustness
  -> backward active-boundary analysis
  -> decision/uncertainty phase maps + objective geometry
  -> blinded PUR-RECOVER V1 Agent benchmark
  -> availability-first PPG2000/PDP-70 five-point wet-lab transfer study
  -> exact frozen-candidate confirmation when PPG700/PPG1000 become available
```

The experimental/public science layer and synthetic decision benchmark are kept strictly separate. `PUR_SIM_V1` is not used as empirical evidence for physical polyurethane rheology.

## Frozen PUR-FRONTIER V1

The complete 928-candidate response snapshot is stored losslessly and SHA256-verified. `scripts/freeze_frontier_v1.py` reconstructs it automatically and regenerates the full frontier from `configs/frontier_v1.json`.

| Layer | Frozen result | Meaning |
|---|---|---|
| L0 property-only | `WO_INV_0419` | closest nominal rheology to the preferred target, but MDI fraction = 34.06 wt% < 35 wt% floor |
| L1 nominal constrained | `WO_INV_0579` | best point-feasible candidate under rheology + chemistry/process gates |
| L2 robust | `WO_INV_0420` | best worst-case candidate after broad-window uncertainty propagation and domain support |

Counts:

```text
928 total candidates
141 nominally feasible
117 robust-admissible
```

The L2 rule is a parameter-free worst-case extension of the same nominal log-space objective. The stored viscosity uncertainty radius is propagated as `q=(1,1,2)` for eta80, eta120 and eta80/eta120, respectively; the ratio receives `2r` because numerator and denominator can move in opposite directions. Full uncertainty intervals must remain inside the broad functional windows, while preferred windows remain the optimisation target rather than a certification envelope.

## Decision-frontier inversion

Among the 117 robust-admissible candidates:

```text
Spearman rho = 0.9851
Kendall tau  = 0.8918
367 / 6786 pairwise inversions = 5.41%
nominal top  = WO_INV_0579
robust top   = WO_INV_0420
```

Thus global ordering remains strongly preserved while the top material decision changes. This is a **decision-frontier inversion**, not a global failure of rheological screening.

A fixed-chemistry PPG700/PPG1000 = 50/50 control over NCO:OH = 1.8-2.5 gives Kendall tau = 1.0 and 0/28 inversions, showing that the robust transformation does not mechanically manufacture ranking inversions.

## Backward design

For the L0 winner's 50/50 PPG700/PPG1000 trajectory,

```text
mdi_parts = 30.3875 * NCO:OH
```

so the 35 wt% MDI floor is crossed at

```text
NCO:OH* = 1.7719836724.
```

Projection onto the frozen 0.1 grid gives the first reachable point at **1.8**, candidate `WO_INV_0420` — the same candidate selected independently by L2 robust ranking.

## Deeper deterministic decision geometry

`FRONTIER-DEPTH V1` studies why the selected decision changes rather than treating the winner as a single immutable point. The current non-Agent core includes:

- MDI-floor decision phase maps;
- nominal-to-robust ranking propagation;
- uncertainty-scaling phase transitions;
- the robustness cliff where no broad-window robust candidate remains;
- objective-weight stability basins;
- a Pareto opportunity set;
- the two-independent-DOF rheology-state geometry implied by `eta80 = eta120 * ratio`.

These analyses remain properties of the frozen synthetic `PUR_SIM_V1` benchmark and are not presented as experimental polyurethane laws.

## PUR-RECOVER V1 Agent

The Agent does not define the gold answer. Primary runs use anonymised candidates/materials and hide rank, scores, mapping files and future wet-lab results. Deterministic tools perform ranking, constraint checks, backward solving, reachability and local sweeps.

The primary metric is **complete_decision_recovery**. A successful run must recover:

- L0 property winner;
- L1 constrained winner;
- L2 robust winner;
- active constraint;
- backward threshold;
- reachable grid point;
- local NCO direction;
- local composition direction.

The formal repeated API benchmark is the next execution stage. Mock/offline runs are tests only and are not manuscript performance results.

### Current vs historical Agent code

**Current paper Agent:** `src/pur_agent/` (`PUR_RECOVER_V1`).

**Historical code:** `src/pur_bridge/agent.py` contains the old E6 / information-gain / experiment-selection pathway. It is retained for provenance and legacy compatibility but must not be used as the current paper Agent implementation.

Read `docs/AGENT_HANDOFF_CURRENT.md` before editing/running Agent code. A copy-paste local-Claude handoff is stored at `docs/CLAUDE_PUR_RECOVER_V1_HANDOFF.md`.

## Secondary mode: PUR-AUDIT V1 (`pur_audit`)

Same blind bundle and frozen contract, different question: explain why L0/L1/L2 differ, quantify how far the MDI floor or the uncertainty scale can move before the robust winner changes, report reachability, objective double-counting, Pareto alternatives, weight stability and contradictions, and propose the hypothesis most worth a wet-lab test. Tools are wrappers over `src/pur_science/depth.py`; the scorer compares against `gold_audit.json` computed by the same functions. See `docs/PUR_AUDIT_V1.md`. Pilot instructions: `docs/PILOT_RUNBOOK.md`.

## Current prospective wet-lab validation

The current laboratory execution design is `docs/VALIDATION_EXPERIMENT_V5.md`. It incorporates the supervisor requirement to prioritise common, fast-to-obtain materials and separates **TDS-based design** from **COA-based batch execution correction**.

The seven polyester candidates from the supplied common-material list were audited. Official, numerically complete manufacturer data were readily retrievable for DYNACOLL 7360 and STEPANPOL PDP-70. Exact public grade TDS could not be reliably retrieved for several HDPOL grades, so no unverified numerical specification is used for them.

### Priority A — frozen common-material five-point experiment

The first experiment is now fixed as:

```text
PPG2000 + STEPANPOL PDP-70 + 4,4'-MDI
```

PDP-70 is selected because it is a liquid, difunctional aromatic polyester polyol with an official OH value of 70 mg KOH/g, explicit polyurethane/reactive-hot-melt use, and simpler handling than a crystalline polyester. DYNACOLL 7360 remains the principal backup.

The five-point matrix is unchanged in structure:

| Role | PPG2000 / PDP-70 | NCO:OH | Purpose |
|---|---:|---:|---|
| `N-` | 50/50 | 1.70 | lower-stoichiometry neighbour |
| `CTR` | 50/50 | 1.80 | centre/reference |
| `N+` | 50/50 | 1.90 | higher-stoichiometry neighbour |
| `C-P` | 60/40 | 1.80 | PPG2000-rich neighbour |
| `C-E` | 40/60 | 1.80 | polyester-rich neighbour |

Each formulation uses **three independent synthesis batches** (`5 x 3 = 15`). Every batch retains paired pre-MDI blend and post-MDI prepolymer samples for `80/90/100/110/120 °C` rheology and Andrade-state analysis.

Nominal design-stage charges use grade-level TDS/theoretical specifications only. Batch COA values are not fed to AI/Agent; they are used by the laboratory only to correct the final MDI mass while preserving the preregistered composition ratio and NCO:OH.

This common-material panel is a real-material transfer study. It does **not** constitute exact experimental validation of `WO_INV_0420`, because the chemistry differs from the frozen synthetic candidate.

### Priority B — exact frozen-candidate confirmation

The previous PPG700/PPG1000 plan is retained as a later strict confirmation when those samples become available. Minimum strict local validation uses `WO_INV_0419 / 0420 / 0421` at PPG700/PPG1000 = 50/50 and NCO:OH = 1.70/1.80/1.90, preferably three independent batches per point.

`docs/VALIDATION_EXPERIMENT_V4.md` is retained as the availability-first selection-stage plan; `docs/VALIDATION_EXPERIMENT_V3.md` is the previous exact-`WO_INV_0420` five-formulation plan; `docs/VALIDATION_EXPERIMENT_V2.md` remains historical single-point provenance.

## Figures

- Figure 2: formulation-specific Andrade temperature response and apparent activation energies.
- Figure 3: free-NCO coupling to viscosity and thermal sensitivity, evaluated within the source-supported temperature range.
- Figure 4: temperature-amplified chemistry contrast, composition-context interaction and published temperature-induced rheological rank reversal.
- **Figure 5: frozen L0/L1/L2 decision frontier, backward boundary, rank propagation and MDI-floor phase behavior.**
- **Figure 6: uncertainty phase transition, robustness cliff, objective-weight stability and rheology-state objective geometry.**
- **Figure 7: formal repeated PUR-RECOVER V1 Agent benchmark — render only from real API run records.**
- **Figure 8: prospective wet-lab validation — current Priority A is the PPG2000/PDP-70 five-point matrix; Priority B is exact-candidate confirmation when available.**

Formal R sources are in `figures/R/`; PNG/PDF/SVG outputs for completed deterministic figures are in `figures/final/`.

## Reproducibility

```bash
git pull
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -e ".[agent,dev]"
pytest

# Regenerate exact deterministic science and completed R figures
python scripts/freeze_frontier_v1.py
python scripts/analyze_frontier_depth_v1.py
Rscript figures/R/render_all_figures.R

# Build the primary blind benchmark
python scripts/build_blind_bundle.py
python scripts/verify_no_leakage.py

# Offline smoke — infrastructure only
python scripts/run_agent_once.py --provider mock --condition pur_agent
python scripts/run_baselines.py --runs 2 --provider mock

# Real API — key stays in the local environment
export OPENAI_API_KEY="..."
export OPENAI_BASE_URL=""       # optional
export OPENAI_MODEL="..."
python scripts/run_agent_benchmark.py --runs 5
python scripts/run_baselines.py --conditions direct_llm tool_llm pur_agent --runs 5

# Formal repeated benchmark after the pilot/config is frozen
# Target 30-50 independent runs per comparable LLM condition if cost permits.

python scripts/evaluate_agent_runs.py results/recover_v1
python scripts/summarize_benchmark.py
```

Never commit a real API credential. Failed/invalid/timeout runs are retained as benchmark outcomes rather than silently deleted.

## Repository map

| Path | Role |
|---|---|
| `docs/RHEOLOGY_SCIENCE_V1.md`, `docs/NON_AGENT_WORKFLOW_V3.md` | source-grounded physical rheology layer |
| `docs/FRONTIER_V1.md`, `configs/frontier_v1.json`, `src/pur_science/` | frozen deterministic L0/L1/L2 frontier |
| `docs/FRONTIER_DEPTH_V1.md`, `results/frontier_depth_v1/` | constraint/uncertainty phase maps, objective geometry, Pareto and stability analyses |
| `results/frontier_v1/` | frozen decision, scores, ranking metrics and preservation control |
| `data/pur_sim_v1/` | 928-design grid + hash-verified frozen response snapshot |
| `docs/AGENT_STRATEGY_V1.md`, `docs/AGENT_HANDOFF_CURRENT.md`, `configs/recover_v1.json`, `src/pur_agent/` | current blinded PUR-RECOVER V1 Agent |
| `docs/CLAUDE_PUR_RECOVER_V1_HANDOFF.md` | developer handoff prompt for local Claude |
| `docs/VALIDATION_EXPERIMENT_V5.md` | current PPG2000/PDP-70 five-point common-material experiment |
| `docs/VALIDATION_EXPERIMENT_V4.md` | previous availability-first selection-stage plan |
| `docs/VALIDATION_EXPERIMENT_V3.md` | previous exact-`WO_INV_0420` five-formulation validation plan |
| `docs/VALIDATION_EXPERIMENT_V2.md` | historical single-point `WO_INV_0579` validation provenance |
| `src/pur_bridge/agent.py`, `legacy/` | historical E6 / old Agent provenance; not the current benchmark |
| `benchmark/`, `gold/`, `results/recover_v1/` | blind inputs, evaluator-only gold and Agent outputs |
| `figures/`, `data/figures/` | manuscript figure sources and render data |
| `manuscript/` | versioned paper drafts and current non-Agent Results |
| `configs/oracle_v2.json`, `results/oracle_v2/` | historical frozen PUR-ORACLE V2 provenance |

## Claim boundary

Experimental/public evidence supports the physical rheology conclusions: formulation-specific temperature sensitivity, free-NCO trends, temperature-amplified chemistry contrast, temperature-induced rheological rank reversal in published patent points, and composition-context effects within their stated evidence limits.

`PUR_SIM_V1` supports finite-space optimisation, constraint propagation, interval robustness, decision-phase analysis, objective-geometry analysis, backward design and blind Agent recovery only. It does not establish a universal optimum over all polyurethane chemistry. The PPG2000/PDP-70 V5 experiment supports common-material transfer/rheology claims but not exact `WO_INV_0420` identity validation; that remains Priority B. Prospective wet-lab results remain outside the primary blind Agent benchmark.