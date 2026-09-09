# data/pur_sim_v1

Synthetic candidate space and frozen response snapshot for the algorithmic benchmark (`PUR_SIM_V1`). Nothing in this directory is experimental evidence.

## Files

| File | Status | Content |
|---|---|---|
| `design_space_928.csv` | frozen design grid | 928 candidate IDs, blend, PPG parts, NCO:OH, nominal MDI parts, MDI fraction. Descriptor-only provenance is recorded in `PROVENANCE.json`. |
| `candidates_full_parts/part_01.b64` ... `part_04.b64` | frozen complete response snapshot | Lossless XZ/base64 representation of the 928-row `PUR_SIM_V1` response table recovered from the original project handoff. |
| `candidates_full.csv` | generated locally | Reconstructed automatically from the four versioned parts by `scripts/freeze_frontier_v1.py`; intentionally not required as a separately maintained source artifact. |
| `RECOVERED_RESPONSE_PROVENANCE.json` | provenance | Original source, selected schema, frozen hash and reconstruction details. |

## Reproducible reconstruction

Run:

```bash
python scripts/freeze_frontier_v1.py
```

If `data/pur_sim_v1/candidates_full.csv` does not exist, the freeze script calls `pur_science.dataio.materialize_pur_sim_v1`, concatenates the four sorted base64 parts, XZ-decompresses them and verifies the reconstructed bytes against:

```text
SHA256 d8623116c6a2f60c9e022e52eeb6540573dd9434b5e507c79701abb55635bcd9
```

A hash mismatch is a hard error; the frontier is not frozen from silently changed data.

## Complete response schema

One row per candidate, 928 rows:

```text
source_candidate_id
blend
nco_oh
mdi_parts
PPG400
PPG700
PPG1000
PPG2000
simulated_eta_80c_pa_s
simulated_eta_120c_pa_s
simulated_ratio_80c_120c
simulated_domain_ratio
simulated_log10_interval_radius
simulated_chemistry_in_domain_flag
```

The response snapshot contains no oracle rank, gold ID or final-decision labels. Blind-bundle generation additionally strips any future columns containing oracle/gold/rank/score/best information.

## Uncertainty convention used by PUR-FRONTIER V1

The stored log10 interval radius `r` reproduces the frozen viscosity intervals as:

```text
log10(eta80)  +/- r
log10(eta120) +/- r
```

Because `ratio = eta80 / eta120`, FRONTIER V1 conservatively propagates the two viscosity intervals as:

```text
log10(ratio) +/- 2r
```

The original source interval columns reproduce this relation to numerical precision across the 928 candidates. This convention is frozen in `configs/frontier_v1.json`.

## Claim boundary

`PUR_SIM_V1` supports only algorithm benchmarking, finite-space optimization, ranking propagation, constraint handling, interval robustness, backward calculation and blind Agent recovery. It must not be described as experimentally discovered polyurethane behavior. Physical rheology claims come from the separately curated experimental/public evidence layer.
