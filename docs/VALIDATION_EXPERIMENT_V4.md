# Prospective wet-lab validation V4 — availability-first common-material design

**Status:** current laboratory planning source of truth after incorporating the supervisor requirement to prioritise common, fast-to-obtain raw materials.

**Teacher requirement:** experimental formulations should preferentially use commonly stocked/requested materials so samples can be obtained quickly and synthesis can start without waiting for unusual grades.

**Uploaded common-material list reviewed:**

- isocyanate: `MDI`
- polyether polyol: `PPG2000`
- polyester polyols: `7360`, `PDP-70`, `HDPOL-320P`, `HDPOL-2000A`, `HDPOL-338A`, `HDPOL-3170`, `HDPOL-2000IPS`
- petroleum resins: `TA 100`, `TM20AS`, `SA100`, `SA120`, `TM85`, `TK 100`
- acrylic resin: `AC1920`

The names alone are not sufficient to assume molecular weight, functionality or hydroxyl number. Formal formulation uses actual TDS/COA/assay data.

## Why V4 changes the execution order

The previous V3 centred on the exact frozen synthetic decision point `WO_INV_0420`, which uses PPG700/PPG1000. Those grades are not in the current common-material list, while MDI and PPG2000 are. Therefore V4 separates two experimental questions instead of forcing an unavailable material substitution into the frozen candidate identity:

1. **Priority A — common-material transfer study:** start quickly with stocked/requestable materials and test the scientific rheology hypotheses in real chemistry.
2. **Priority B — strict frozen-candidate confirmation:** retain the exact PPG700/PPG1000 `WO_INV_0420` neighbourhood for later confirmatory testing when those samples are available.

The common-material panel must never be described as an exact experimental validation of `WO_INV_0420`; it is a transfer/interaction study.

## Priority A0 — raw-material qualification gate

Request immediately:

- 4,4'-MDI / the laboratory's intended MDI grade;
- PPG2000;
- two or three of the listed polyester polyols for which samples can be supplied fastest.

Before choosing the formal polyester grade, collect for each candidate where available:

- hydroxyl number (mg KOH/g);
- functionality;
- water content;
- acid value;
- viscosity and/or melting/handling temperature;
- molecular-weight information if supplied;
- lot/grade identity;
- for MDI, NCO content/purity.

### Polyester-X selection rule

Choose **one** polyester polyol (`Polyester-X`) for the formal common-material matrix using a pre-declared suitability gate:

1. sample is immediately available or fastest to obtain;
2. OH number is known from TDS/COA or can be assayed;
3. material can be dried and handled reproducibly under the planned 70–110 °C process;
4. no unknown reactive functionality that prevents a controlled NCO:OH calculation;
5. water/acid information is available or measurable;
6. among materials passing 1–5, prefer the grade with the clearest documentation and simplest laboratory handling.

Do **not** choose a grade after seeing viscosity results. Record rejected grades and reasons.

## Priority A1 — one-batch process shakedown

Before the formal matrix, run one small **method-qualification** batch with:

```text
polyol = PPG2000
isocyanate = MDI
NCO:OH = 1.80
```

Use actual lot OH number and MDI NCO content to calculate the charge. This batch is for checking drying, charging, mixing, endpoint assay, sampling and rheometer handling. It is not counted as one of the three independent formal replicates unless it was prospectively declared and executed under the final protocol without procedural changes.

## Priority A2 — formal common-material five-point matrix

Use only three reactive raw-material identities in the core matrix:

```text
MDI + PPG2000 + Polyester-X
```

Keep the same interpretable local cross geometry as the previous plan:

| Role | PPG2000 / Polyester-X (polyol parts) | NCO:OH | Purpose |
|---|---:|---:|---|
| `N-` | 50 / 50 | 1.70 | lower-stoichiometry neighbour |
| `CTR` | 50 / 50 | 1.80 | centre/reference formulation |
| `N+` | 50 / 50 | 1.90 | higher-stoichiometry neighbour |
| `C-P` | 60 / 40 | 1.80 | PPG2000-rich composition neighbour |
| `C-E` | 40 / 60 | 1.80 | polyester-rich composition neighbour |

For every formulation, calculate MDI from the **actual equivalent OH content** of the selected lots; do not reuse the old PPG700/PPG1000 MDI masses.

Formal replication:

```text
5 formulations x 3 independent syntheses = 15 independent batches
```

This design directly tests:

- the real NCO:OH response around 1.8;
- a polyether-to-polyester composition axis;
- whether chemistry and stoichiometry interact locally;
- whether reaction with MDI amplifies or reshapes pre-existing blend rheology.

## Paired pre-MDI / post-MDI sampling

For every formal batch:

1. prepare and dry the full PPG2000/Polyester-X blend plus sufficient excess for a paired pre-MDI aliquot;
2. under dry nitrogen, remove and seal the pre-MDI blend aliquot;
3. recalculate MDI using the actual remaining polyol mass if the removed mass differs from the planned value;
4. add MDI and complete prepolymer synthesis;
5. retain the post-reaction prepolymer as the paired sample.

This creates a within-batch comparison:

```text
pre-MDI polyol blend -> post-MDI NCO-terminated prepolymer
```

## Core synthesis controls

- dry polyols/blends before reaction; target residual water should be documented and kept low enough for controlled isocyanate chemistry (the prior protocol used <=0.05 wt% as a practical target where measurable);
- use dry nitrogen protection;
- calculate MDI from actual OH number and actual/assayed NCO content;
- approximately 110 °C reaction and ~3 h may be used as a starting process window, but endpoint is judged by stable NCO rather than elapsed time alone;
- begin NCO checks near 2 h and continue at fixed intervals until stable according to the laboratory's validated method;
- record actual batch masses, temperature history, mixing and endpoint values.

## Rheology measurements

For both paired stages (`pre-MDI` and `post-MDI`), measure:

```text
80, 90, 100, 110, 120 °C
```

Use the same instrument geometry/method across the matrix. At each temperature use two technical readings initially; add a third when the predefined repeatability criterion is not met. Independent synthesis batches, not repeated instrument readings, define biological/material replication.

For each formulation x batch x stage, fit:

```text
ln(eta) = A + B/T
Ea,app = R*B
```

Primary experimental outputs:

- eta(T) curve;
- eta80 and eta120;
- eta80/eta120;
- Ea,app;
- terminal NCO content;
- batch-to-batch reproducibility;
- pre/post reaction amplification or reshaping.

## Main scientific tests in Priority A

### Test 1 — stoichiometric response

At 50/50 PPG2000/Polyester-X, compare `N-`, `CTR`, `N+` to estimate the local response of eta(T) and Ea,app to NCO:OH.

### Test 2 — chemistry/composition response

At NCO:OH = 1.80, compare `C-P`, `CTR`, `C-E` to estimate the local response to polyether/polyester composition.

### Test 3 — chemistry x stoichiometry hypothesis

The five-point axial design provides a strong local screening of both axes but does **not by itself fully identify an interaction term** because it does not contain factorial corner combinations. If the Priority A data show a meaningful composition effect and the lab can support two additional formulations, add a preregistered interaction extension using two opposite corners (for example one PPG2000-rich/low-NCO and one polyester-rich/high-NCO point). If a formal interaction coefficient is a major manuscript claim, use a full 2x2 corner design plus centre rather than inferring interaction from the axial cross alone.

This distinction must be respected in the manuscript.

## Optional application layer — only after core prepolymer study is stable

Do not mix tackifier effects into the first reactive-polyol matrix. The listed petroleum resins (`TA 100`, `TM20AS`, `SA100`, `SA120`, `TM85`, `TK 100`) are valuable later as an application-rheology layer, but adding them at the beginning would confound polyol chemistry, stoichiometry and non-reactive resin loading.

After Priority A is stable, choose one common petroleum resin using documented compatibility/softening-point/process criteria and run a small preregistered loading series if needed.

`AC1920` should also remain outside the first core matrix until its TDS clarifies functionality, compatibility and intended role.

## Priority B — exact frozen-candidate confirmation

When PPG700 and PPG1000 samples become available, retain a strict computational transfer test centred on the frozen decision:

```text
PPG700/PPG1000 = 50/50
NCO:OH = 1.80
WO_INV_0420
```

Minimum strict local confirmation:

| Role | Frozen candidate | PPG700/PPG1000 | NCO:OH |
|---|---|---:|---:|
| `N-` | `WO_INV_0419` | 50/50 | 1.70 |
| `OPT` | `WO_INV_0420` | 50/50 | 1.80 |
| `N+` | `WO_INV_0421` | 50/50 | 1.90 |

Prefer three independent batches per formulation (9 syntheses). If resources permit, restore the two composition neighbours from V3 for a full 15-batch strict local matrix.

Priority B is the experiment that can support the statement that the frozen PUR_SIM_V1 decision neighbourhood transferred to real material. Priority A cannot substitute for this exact claim.

## Relationship to the paper and Agent

```text
real/public rheology evidence
-> deterministic PUR_SIM_V1 decision science
-> blind PUR-RECOVER / PUR-AUDIT Agent
-> Priority A common-material transfer study
-> Priority B exact frozen-candidate confirmation when materials are available
```

Primary Agent input remains strictly isolated from all prospective wet-lab outcomes.

### Claim boundary

- Priority A supports real experimental statements about common-material rheology, polyether/polyester composition response, NCO:OH response, and pre/post-MDI transformation.
- Priority A does **not** validate the exact identity of `WO_INV_0420` because its chemistry differs from the frozen candidate.
- Priority B supports the strict computational-to-physical candidate transfer claim.
- Neither experiment turns `PUR_SIM_V1` synthetic responses into experimental evidence.

## Immediate sample-request priority

1. MDI;
2. PPG2000;
3. fastest two or three polyester-polyol samples from the provided list, together with TDS/COA;
4. defer petroleum-resin and acrylic-resin requests until the core reactive-polyol experiment is underway unless samples are routinely supplied at no additional delay.

The first decision after sample arrival is selection of `Polyester-X` by the preregistered qualification gate above, not by observed rheology performance.
