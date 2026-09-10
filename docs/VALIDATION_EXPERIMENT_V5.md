# Prospective wet-lab validation V5 — common-material five-point plan

**Status:** current wet-lab execution design after the supervisor requirement to prioritise common, fast-to-obtain raw materials and to use TDS for design-stage material selection. Batch-specific COA data are **not** used as AI/Agent inputs; they are used only at execution time for stoichiometric charge correction.

## 1. Material-screening conclusion

The uploaded common-material list contains seven polyester-polyol candidates: `7360`, `PDP-70`, `HDPOL-320P`, `HDPOL-2000A`, `HDPOL-338A`, `HDPOL-3170`, and `HDPOL-2000IPS`.

A web/TDS audit was performed before fixing the five-point matrix.

| Grade | Public evidence retrieved | Key usable information | Decision for first five-point matrix |
|---|---|---|---|
| DYNACOLL 7360 | Official Evonik TDS | crystalline polyester polyol; OH 27–34 mg KOH/g; acid <=2; Mw ~3500; mp 55 °C; viscosity ~2 Pa·s at 80 °C; reactive-hot-melt application | strong backup; not first choice because crystallinity/melting history adds another rheological variable and OH differs strongly from PPG2000 |
| STEPANPOL PDP-70 | Official Stepan product bulletin/page | linear aromatic polyester polyol; OH 70 mg KOH/g; functionality 2; EW 801; water <=0.05 wt%; acid <=1; liquid at 25 °C; viscosity ~1900 cP at 25 °C; reactive-hot-melt use; polyether/isocyanate compatibility noted | **selected for first matrix** |
| HDPOL-320P | Huide manufacturer identity + patent evidence | amorphous polyester polyol; commercial Huide grade; patent reports Mw ~2000 and use in reactive PU hot-melt systems | scientifically attractive, but exact public grade TDS was not reliably retrievable; keep as backup pending supplier TDS |
| HDPOL-2000IPS | Patent evidence | listed as liquid polyester polyol and temperature-sensitive PUR-hot-melt grade; cited range 0.4–1.0 Pa·s at 120 °C and 10–30 Pa·s at 60 °C for the temperature-sensitive class | useful future rheology comparator; exact official grade TDS not retrieved |
| HDPOL-2000A | exact public TDS not reliably retrieved | no numerical specification used | do not use for preregistered charge calculation until supplier TDS is available |
| HDPOL-338A | exact public TDS not reliably retrieved | no numerical specification used | do not use for preregistered charge calculation until supplier TDS is available |
| HDPOL-3170 | exact public TDS not reliably retrieved | no numerical specification used | do not use for preregistered charge calculation until supplier TDS is available |

Primary public sources used for this audit:

- Evonik DYNACOLL 7360 TDS: https://products.evonik.com/assets/84/07/TDS_DYNACOLL_7360_EN_EN_Asset_1208407.pdf
- Stepan STEPANPOL PDP-70 product bulletin: https://www.stepan.com/content/dam/stepan-dot-com/webdam/website-product-documents/product-bulletins/polymers/STEPANPOLPDP70.pdf
- Huide polyester-polyol manufacturer page: https://en.shhdsz.com/index.php?catid=46
- HDPOL-320P commercial identity / reactive-hot-melt use: https://patents.google.com/patent/WO2026102758A1/en
- HDPOL-2000IPS hot-melt/temperature-sensitive evidence: https://patents.google.com/patent/CN116265556A/en

## 2. Why PDP-70 is selected

`PDP-70` is selected as the first `Polyester-X` because it gives the cleanest availability-first experiment with the least avoidable confounding:

1. an official manufacturer technical bulletin is public and numerically complete;
2. it is a **liquid** polyester polyol at room temperature, simplifying weighing, drying, mixing and repeat synthesis;
3. it is difunctional and has a defined OH value (70 mg KOH/g), so NCO:OH can be calculated transparently;
4. it is explicitly positioned for polyurethane adhesives/reactive hot melts and notes compatibility with some polyethers and isocyanates;
5. unlike crystalline 7360, it avoids introducing a melt/crystallisation transition as an extra variable in the primary 80–120 °C rheology experiment.

DYNACOLL 7360 remains the preferred backup if PDP-70 sample supply is slower than expected or if a crystalline-polyester comparison becomes a deliberate second-stage question.

## 3. TDS vs COA rule

### Design / AI layer

Use stable grade-level information from TDS/manufacturer literature to define the experiment. Do **not** train or condition the Agent on batch COA values.

### Execution layer

Once a physical lot arrives, laboratory personnel use that lot's COA/assay only to correct the exact MDI charge while preserving the preregistered NCO:OH. COA variation must not change which five formulations are run.

Thus:

```text
TDS -> select/freeze formulation identities and nominal design
COA -> batch-specific stoichiometric correction at the bench
```

## 4. Frozen first-stage five-point matrix

Reactive raw materials:

```text
PPG2000 + STEPANPOL PDP-70 + 4,4'-MDI
```

Five points remain exactly the original local-cross design:

| Role | PPG2000 / PDP-70 (polyol wt parts) | NCO:OH | Main question |
|---|---:|---:|---|
| `N-` | 50 / 50 | 1.70 | lower-stoichiometry response |
| `CTR` | 50 / 50 | 1.80 | centre/reference |
| `N+` | 50 / 50 | 1.90 | higher-stoichiometry response |
| `C-P` | 60 / 40 | 1.80 | PPG2000-rich composition response |
| `C-E` | 40 / 60 | 1.80 | polyester-rich composition response |

Formal replication remains:

```text
5 formulations x 3 independent synthesis batches = 15 independent syntheses
```

No sixth formulation is added to the first-stage experiment.

## 5. Nominal design-stage charge calculation

The following numbers are **nominal planning values**, not batch-final COA values.

Design assumptions:

- PPG2000: difunctional, nominal Mn ~2000 -> theoretical OH number `56.1 mg KOH/g` for planning;
- PDP-70: official TDS OH number `70 mg KOH/g`, functionality `2.0`;
- 4,4'-MDI: nominal/theoretical NCO content `33.6 wt%` for planning.

For a blend with masses `m_i` (g) and OH numbers `OH_i` (mg KOH/g):

```text
OH equivalents = sum(m_i * OH_i / 56100)
required NCO equivalents = (NCO:OH) * OH equivalents
MDI mass = required NCO equivalents * (42.02 / w_NCO)
```

where `w_NCO` is the MDI NCO mass fraction.

### 100-part polyol basis

| Role | PPG2000 | PDP-70 | NCO:OH | nominal MDI parts | nominal MDI fraction of polyol+MDI |
|---|---:|---:|---:|---:|---:|
| `N-` | 50 | 50 | 1.70 | 23.894 | 19.29% |
| `CTR` | 50 | 50 | 1.80 | 25.299 | 20.19% |
| `N+` | 50 | 50 | 1.90 | 26.705 | 21.08% |
| `C-P` | 60 | 40 | 1.80 | 24.742 | 19.83% |
| `C-E` | 40 | 60 | 1.80 | 25.857 | 20.54% |

These MDI fractions are expected to differ from the old synthetic `WO_INV_0420` neighbourhood. This is intentional: the present common-material experiment is a real-material transfer study, not an attempt to relabel PPG2000/PDP-70 as the synthetic PPG700/PPG1000 candidate.

### Nominal 300 g final-prepolymer batches

| Role | PPG2000 (g) | PDP-70 (g) | MDI (g) | final mass (g) |
|---|---:|---:|---:|---:|
| `N-` | 121.07 | 121.07 | 57.86 | 300.00 |
| `CTR` | 119.71 | 119.71 | 60.57 | 300.00 |
| `N+` | 118.39 | 118.39 | 63.23 | 300.00 |
| `C-P` | 144.30 | 96.20 | 59.50 | 300.00 |
| `C-E` | 95.35 | 143.02 | 61.63 | 300.00 |

At the bench, replace the nominal OH/NCO values in the calculation with the physical lot COA/assay values; keep the 50/50 or 60/40 or 40/60 polyol ratio and the preregistered NCO:OH fixed.

## 6. Paired pre-MDI sample

For each independent batch, prepare an additional `12.00 g` of the same polyol blend before MDI addition and remove it after drying under the same history.

| Role | extra PPG2000 for paired sample (g) | extra PDP-70 (g) |
|---|---:|---:|
| `N-` | 6.00 | 6.00 |
| `CTR` | 6.00 | 6.00 |
| `N+` | 6.00 | 6.00 |
| `C-P` | 7.20 | 4.80 |
| `C-E` | 4.80 | 7.20 |

The paired comparison remains:

```text
pre-MDI polyol blend -> post-MDI NCO-terminated prepolymer
```

## 7. Core laboratory workflow

1. Weigh PPG2000 and PDP-70 at the frozen ratio, including the 12 g paired-sample excess.
2. Dry under the laboratory's validated vacuum/dehydration procedure; document water where measurable.
3. Under dry nitrogen, remove and seal the paired pre-MDI aliquot.
4. Use that physical lot's COA/assay OH and MDI NCO values to recalculate only the exact MDI mass while preserving the frozen NCO:OH.
5. Add MDI under dry nitrogen and synthesize the NCO-terminated prepolymer.
6. Follow NCO content to a stable endpoint rather than relying only on clock time.
7. Measure both pre-MDI and post-MDI material at `80, 90, 100, 110, 120 °C` using the same rheology protocol.
8. Fit `ln(eta) = A + B/T` and calculate `Ea,app = R*B` for each formulation x independent batch x stage.

## 8. Primary scientific comparisons

The first-stage five-point experiment is intended to estimate:

- the local stoichiometric response from `N- -> CTR -> N+`;
- the polyether/polyester composition response from `C-P -> CTR -> C-E`;
- whether MDI reaction amplifies or reshapes the pre-existing composition-dependent rheology;
- batch-to-batch reproducibility of those trends.

The five-point axial cross does not by itself identify a full chemistry x stoichiometry interaction coefficient. Do not make a formal interaction claim without additional factorial corners.

## 9. Claim boundary

This V5 experiment supports real-material statements about PPG2000/PDP-70/MDI rheology and local transfer of the decision logic. It does **not** constitute exact experimental validation of the synthetic `WO_INV_0420` identity.

The old PPG700/PPG1000 `WO_INV_0420` neighbourhood remains a later strict frozen-candidate confirmation if those raw materials become available.

Prospective wet-lab data remain excluded from the primary PUR-RECOVER/PUR-AUDIT Agent input.
