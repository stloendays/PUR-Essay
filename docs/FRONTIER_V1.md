# PUR-FRONTIER V1 — deterministic decision frontier

Definition source: `configs/frontier_v1.json`. Implementation: `src/pur_science/`. Output after the complete table is restored: `results/frontier_v1/` via `scripts/freeze_frontier_v1.py`.

**Current status: PRE_FREEZE_AWAITING_COMPLETE_RESPONSE_TABLE.** The scientific rule is fixed before reading the missing full 928-response table; the L0 and L2 winners are not yet treated as gold.

PUR-FRONTIER V1 builds on the frozen PUR-ORACLE V2 record without rewriting the historical files.

## Question

The decision problem is not simply "which candidate has the best predicted viscosity?" It is

```text
property optimum -> nominal feasibility -> robust decision -> backward boundary -> reachability
```

The purpose of the frontier is to separate these layers and determine exactly why a decision changes.

## Layers

| Layer | Candidate set | Score | Role |
|---|---|---|---|
| L0 property-only | all 928 candidates | `J = Σ_k w_k log10(y_k/c_k)^2` | identifies the unconstrained rheological optimum |
| L1 nominal constrained | candidates passing point-response broad/preferred windows, NCO:OH, MDI fraction and chemistry-domain gates | same `J` | identifies the best formulation under the frozen nominal chemistry/process rules |
| L2 robust | L1 candidates with `domain_ratio <= 1.0` | `J_robust = Σ_k w_k (|log10(y_k/c_k)| + r)^2` | minimises the worst-case objective over the frozen response interval |

The tie-break remains: higher broad margin, then lower domain ratio, then lexical candidate ID.

### Why uncertainty is not another nominal hard gate

The complete deterministic candidate response is the nominal state. Its feasibility is therefore judged from the point response plus chemistry/process constraints. The uncertainty radius is propagated only after nominal feasibility is established.

For each response, the frozen interval is

```text
log10(y) ± r
```

and the worst possible absolute log-distance from the preferred centre is

```text
|log10(y/c)| + r.
```

Therefore

```text
J_robust = Σ_k w_k (|log10(y_k/c_k)| + r)^2
```

is a parameter-free minimax extension of the nominal objective. No additional uncertainty weight, posterior probability or hand-tuned penalty is introduced.

The previous pre-freeze draft also required the entire uncertainty interval to remain inside every preferred window. That rule has been removed before any FRONTIER gold was frozen. Such containment is too close to a separate uncertainty-certification task and can reject candidates solely because the interval is wide even when the complete-data response is a valid nominal formulation. Interval containment is now a diagnostic only.

For context, even a perfectly centred candidate could fit wholly inside all three preferred windows only if the common log10 radius were no larger than the narrowest preferred half-width. The three centred half-widths are approximately 0.199 for eta80, 0.151 for eta120 and 0.066 for the eta80/eta120 ratio. This illustrates why preferred-window containment would be a very stringent certification rule rather than a neutral robustness ranking.

## Active constraint

For the L0 winner, the deterministic audit reports every failed nominal gate. The primary backward calculation is attached to the MDI-fraction lower bound when that is the active formulation boundary.

The nominal constraint priority used for reporting is:

```text
mdi_fraction -> nco_oh -> chemistry_in_domain -> broad windows -> preferred windows
```

Uncertainty-interval containment is no longer part of the nominal gate list.

## Backward design

On the real frozen design grid, every blend obeys

```text
mdi_parts = k_blend * NCO:OH
```

exactly. With polyol basis `B = 100` and MDI-fraction floor `f = 0.35`, the continuous threshold is

```text
n* = f * B / (k_blend * (1 - f)).
```

For the 50/50 PPG700 + PPG1000 blend, `k = 30.3875`, giving

```text
NCO:OH* = 1.7720.
```

Projection onto the frozen 0.1-spaced NCO:OH grid gives the first reachable point at **1.8**, corresponding to `WO_INV_0420`. The neighbouring 1.7 point, `WO_INV_0419`, has an MDI fraction of about 34.06 wt% and therefore lies below the 35 wt% floor.

This backward result is verified from the real 928-row design grid and does not depend on the missing response columns.

## Local trends

After L2 is computed, local trends are evaluated around the robust winner; if L2 is unavailable they can be evaluated diagnostically around L1.

- `nco_direction`: eta80 response as NCO:OH increases along the same blend.
- `composition_direction`: eta80 response as the higher-MDI-demand component increases within the same two-component family at fixed NCO:OH.

Directions are inferred from the full local sweep (`increase`, `decrease`, `flat`, or `mixed`), not from one selected pair.

## Pre-freeze hypotheses versus gold

The repository previously documented the following expectations:

- L0 property-only hypothesis: `WO_INV_0419`;
- historical constrained decision: `WO_INV_0579`;
- earlier robust hypothesis: `WO_INV_0420`;
- active boundary hypothesis: MDI fraction;
- backward threshold: 1.772 -> reachable grid 1.8.

Only the historical ORACLE V2 result and the design-grid backward calculation are already frozen/verified artifacts. **No L2 winner is predetermined in the current FRONTIER config.** `WO_INV_0420` is retained only as a prior hypothesis and as the first reachable point on the 50/50 backward trajectory. The full-table calculation is allowed to select a different robust winner.

## Reproduction status and blocker

The repository currently contains:

- the real 928-row descriptor/design grid, `data/pur_sim_v1/design_space_928.csv`;
- the frozen historical ORACLE V2 result;
- a 10-row feasible ranked snapshot, `data/oracle_top30_compact.csv`.

It does **not** contain the complete 928-row PUR_SIM_V1 response table with eta80, eta120, ratio, uncertainty radius and domain descriptors. The old v0.7 response table is generated by a different model and must not be substituted.

Consequently:

- the backward threshold and reachability can already be verified;
- the full L0 ranking cannot yet be recomputed;
- the full L1 ranking under the corrected point-feasibility definition cannot yet be recomputed;
- the L2 minimax winner cannot yet be frozen;
- a final Figure 5 that names L0/L2 winners must wait for the exact response table.

When the original table is restored at `data/pur_sim_v1/candidates_full.csv`, run:

```bash
python scripts/freeze_frontier_v1.py
```

The script records hashes, computes all layers and reports disagreements with prior hypotheses without modifying the input data.

## Claim boundary

PUR_SIM_V1 is a synthetic benchmark space. FRONTIER V1 supports finite-space optimisation, constraint propagation, deterministic interval robustness, backward calculation and reachability. It is not experimental evidence for polyurethane rheology.
