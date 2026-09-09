# data/pur_sim_v1

Synthetic candidate space and frozen response snapshot for the `PUR_SIM_V1` algorithmic benchmark. Nothing in this directory is experimental evidence.

## Files

| File | Status | Content |
|---|---|---|
| `design_space_928.csv` | frozen design grid | 928 candidate IDs, blend, PPG parts, NCO:OH, nominal MDI parts and MDI fraction. |
| `candidates_full.csv.xz.b64.part00` ... `.part03` | frozen response snapshot | Lossless XZ/base64 shards of the complete 928-row response table. |
| `candidates_full.csv` | generated locally | Reconstructed and hash-verified by `pur_science.dataio.materialize_pur_sim_v1`; not maintained as a separate source file. |
| `PROVENANCE.json` | provenance | Synthetic benchmark provenance and design-space metadata. |

## Reproduction

Run:

```bash
python scripts/freeze_frontier_v1.py
```

If `candidates_full.csv` is absent, the materializer concatenates the contiguous `.part00` ... `.part03` shards, decodes base64, XZ-decompresses the bytes and checks

```text
SHA256 d8623116c6a2f60c9e022e52eeb6540573dd9434b5e507c79701abb55635bcd9
```

A mismatch is a hard error.

## Complete response schema

The reconstructed table has 928 rows with one row per candidate and includes:

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

The frozen response snapshot contains no final oracle rank, gold decision ID or best-candidate flag.

## Uncertainty convention used by PUR-FRONTIER V1

The stored candidate radius `r` is propagated as

```text
log10(eta80)  +/- r
log10(eta120) +/- r
log10(eta80/eta120) +/- 2r
```

because the conservative ratio bound combines numerator and denominator uncertainties in opposite directions. This convention is frozen in `configs/frontier_v1.json`.

## Current frozen use

The reconstructed table is the input for PUR-FRONTIER V1, which currently gives:

```text
928 total
141 nominally feasible
117 robust-admissible
L0 WO_INV_0419
L1 WO_INV_0579
L2 WO_INV_0420
```

See `docs/FRONTIER_V1.md` and `results/frontier_v1/` for the decision definition and frozen outputs.

## Claim boundary

`PUR_SIM_V1` supports algorithm benchmarking, finite-space optimization, ranking propagation, constraint handling, interval robustness, backward calculation and blind Agent recovery. It must not be described as an experimentally discovered physical law.
