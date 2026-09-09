# PUR_SIM_V1 response recovery audit

Status: **RECOVERED AND HASH-LINKED TO THE CURRENT FROZEN SNAPSHOT**

This audit resolves the earlier statement that the complete 928-row PUR_SIM_V1 response table was missing. The error was file identification: the uploaded historical `v07_inverse_design.zip` contains two different 928-row WO candidate CSVs, one from the old v0.7 predictor and one carrying the deterministic synthetic PUR_SIM_V1 responses.

## Historical archive

Uploaded archive SHA256:

```text
v07_inverse_design.zip
9cb2c24117528a5639bfd67c0e0b7c090ab487bb6389ef40cd8e76a3197951b3
```

Two distinct 928-row members are present:

| ZIP member | Shape | SHA256 | Meaning |
|---|---:|---|---|
| `v07_inverse_design/v07_wo_inverse_design_candidates.csv` | 928 x 26 | `f07a27fa3772d5898b1da8437bdd6f171f4ba2c3e4e307946d7baca6f6f0c4b3` | old v0.7 ML candidate/prediction table |
| `v07_inverse_design/v07_wo_inverse_design_candidates_模拟.csv` | 928 x 51 | `d623755189481b38a629276c37b85b49e0634901f8e338196677a08b32593abd` | deterministic `PUR_SIM_V1` response table |

The 51-column table explicitly contains `simulation_protocol_id = PUR_SIM_V1`, `synthetic_scenario = True`, simulated eta80/eta120/ratio values, response intervals, uncertainty radius and domain diagnostics. It also retains the old v0.7 response fields separately, which makes the two response systems directly distinguishable.

## Numerical fingerprint

For `WO_INV_0579`, the recovered PUR_SIM_V1 response is approximately:

```text
eta80  = 3.442695 Pa s
eta120 = 0.409765 Pa s
ratio  = 8.401631
```

while the retained old frozen v0.7 response on the same row is approximately:

```text
eta80  = 9.970288 Pa s
eta120 = 8.222226 Pa s
ratio  = 1.212602
```

Therefore the recovered simulated response columns are not a relabeling of the v0.7 predictions.

## Hash link to the repository snapshot

The current repository stores a minimal 14-column canonical snapshot rather than all 51 historical columns. Selecting exactly these columns from the recovered 51-column archive table and serializing them as CSV:

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

produces SHA256:

```text
d8623116c6a2f60c9e022e52eeb6540573dd9434b5e507c79701abb55635bcd9
```

This is exactly the SHA256 frozen by `src/pur_science/dataio.py` and recorded by `results/frontier_v1/manifest.json`. The multipart XZ/base64 representation is therefore a hash-verified canonical projection of the historical PUR_SIM_V1 table.

A second audit compared all 28 shared scientific columns between the recovered 51-column table and the local 29-column Oracle candidate-space artifact after sorting by candidate ID. Every compared field matched exactly; maximum numerical difference was zero at the stored precision.

## Consequence

The complete PUR_SIM_V1 response benchmark is no longer treated as missing. PUR-FRONTIER V1 can remain frozen and reproducible. The old v0.7 response table remains a separate legacy model output and must not be substituted for PUR_SIM_V1.

## Claim boundary

`PUR_SIM_V1` is a deterministic synthetic benchmark. Recovery of its original table restores the algorithmic decision benchmark; it does not convert synthetic response values into experimental polyurethane evidence. Physical rheology claims continue to require source measurements and prospective experiments.
