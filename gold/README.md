# gold/ — evaluator-only

Frozen gold decisions and anonymisation mappings written by `scripts/freeze_frontier_v1.py`
and `scripts/build_blind_bundle.py`. Never copied into a blind bundle. The Agent runtime
(`pur_agent.data_access.BundleReader`) refuses every path under this directory, and
`scripts/verify_no_leakage.py` fails if any of its content appears in a blind bundle.

Generated files (git-ignored):

- `recover_v1/gold_decision.json` — named FRONTIER V1 decision plus full rankings
- `recover_v1/gold_decision_blind.json` — the same decision expressed in anonymous IDs
- `recover_v1/gold_mapping.json` — anonymous -> source ID and material mappings, seed, hashes
