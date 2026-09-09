# data/pur_sim_v1

Synthetic candidate space for the algorithmic benchmark (PUR_SIM_V1). Nothing in this
directory is experimental evidence.

## Files

| File | Status | Content |
|---|---|---|
| `design_space_928.csv` | present, real design grid | 928 candidate IDs, blend, PPG parts, NCO:OH, nominal MDI parts, MDI fraction. Descriptors only. Provenance in `PROVENANCE.json`. |
| `candidates_full.csv` | **missing – must be supplied** | The complete PUR_SIM_V1 response table used to freeze PUR-ORACLE V2. Not in the repository, its history, or on the local machine (see `docs/PROJECT_STATE_AUDIT.md` §10). |

## Required schema of `candidates_full.csv`

One row per candidate, 928 rows. Column names as consumed by `configs/frontier_v1.json`:

```text
source_candidate_id            WO_INV_0001 ...
blend                          e.g. PPG1000:50+PPG700:50
nco_oh                         1.5 ... 3.0
mdi_parts                      nominal 4,4'-MDI parts per 100 polyol parts
PPG400, PPG700, PPG1000, PPG2000   parts (optional; parsed from blend if absent)
simulated_eta_80c_pa_s
simulated_eta_120c_pa_s
simulated_ratio_80c_120c
simulated_domain_ratio
simulated_log10_interval_radius
simulated_chemistry_in_domain_flag   true/false
```

Extra columns are allowed. Any column whose name contains `oracle`, `gold`, `rank`, `score`
or `is_best` is stripped before the blind bundle is built. The freeze script validates the
schema, checks that the descriptor columns agree with `design_space_928.csv`, and records the
SHA256 of the file in every downstream artifact.

## Claim boundary

PUR_SIM_V1 supports only: algorithm benchmark, finite-space optimisation, ranking
propagation, constraint handling, backward calculation and blind Agent recovery. It must not
be described as an experimentally discovered physical law.
