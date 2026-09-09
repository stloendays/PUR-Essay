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
  -> reachability
  -> blinded PUR-RECOVER V1 Agent benchmark
  -> prospective wet-lab validation
```

The experimental/public science layer and synthetic decision benchmark are kept strictly separate. `PUR_SIM_V1` is not used as empirical evidence for physical polyurethane rheology.

## Frozen PUR-FRONTIER V1

The complete 928-candidate response snapshot is now stored losslessly and SHA256-verified. `scripts/freeze_frontier_v1.py` reconstructs it automatically and regenerates the full frontier from `configs/frontier_v1.json`.

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

## Figures

- Figure 2: formulation-specific Andrade temperature response and apparent activation energies.
- Figure 3: free-NCO coupling to viscosity and thermal sensitivity.
- Figure 4: temperature-amplified chemistry contrast and composition-context interaction.
- **Figure 5: frozen L0/L1/L2 decision frontier, backward boundary and nominal-to-robust rank propagation.**
- Figure 6: reserved for the repeated PUR-RECOVER Agent benchmark.

Formal R sources are in `figures/R/`; PNG/PDF/SVG outputs are in `figures/final/`.

## Reproducibility

```bash
git pull
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -e ".[agent,dev]"
pytest

# Regenerate the exact deterministic gold and Figure 5
python scripts/freeze_frontier_v1.py
Rscript figures/R/render_all_figures.R

# Build the blind benchmark
python scripts/build_blind_bundle.py
python scripts/verify_no_leakage.py

# Offline smoke
python scripts/run_agent_once.py --provider mock --condition pur_agent

# Real API — key stays in the environment
export OPENAI_API_KEY="..."
export OPENAI_BASE_URL=""       # optional
export OPENAI_MODEL="..."
python scripts/run_agent_benchmark.py --runs 20
python scripts/run_baselines.py --runs 20
python scripts/summarize_benchmark.py
```

The current CI test suite passes and the Figure workflow rebuilds the frontier from the hash-verified response snapshot before rendering Figure 5.

## Repository map

| Path | Role |
|---|---|
| `docs/RHEOLOGY_SCIENCE_V1.md`, `docs/NON_AGENT_WORKFLOW_V3.md` | source-grounded physical rheology layer |
| `docs/FRONTIER_V1.md`, `configs/frontier_v1.json`, `src/pur_science/` | frozen deterministic L0/L1/L2 frontier |
| `results/frontier_v1/` | frozen decision, scores, ranking metrics and preservation control |
| `data/pur_sim_v1/` | 928-design grid + hash-verified frozen response snapshot |
| `docs/AGENT_STRATEGY_V1.md`, `configs/recover_v1.json`, `src/pur_agent/` | blinded Agent strategy |
| `benchmark/`, `gold/`, `results/recover_v1/` | blind inputs, evaluator-only gold and Agent outputs |
| `figures/`, `data/figures/` | manuscript figure sources and render data |
| `manuscript/` | versioned paper drafts |
| `configs/oracle_v2.json`, `results/oracle_v2/` | historical frozen PUR-ORACLE V2 provenance |

## Claim boundary

Experimental/public evidence supports the physical rheology conclusions: formulation-specific temperature sensitivity, free-NCO trends, temperature-amplified chemistry contrast and composition-context effects.

`PUR_SIM_V1` supports finite-space optimisation, constraint propagation, interval robustness, backward design and blind Agent recovery only. It does not establish a universal optimum over all polyurethane chemistry. Prospective wet-lab results remain outside the primary blind Agent benchmark.
