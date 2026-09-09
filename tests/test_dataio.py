from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from pur_science.dataio import EXPECTED_CANDIDATE_SHA256, materialize_pur_sim_v1

ROOT = Path(__file__).resolve().parents[1]


def test_frozen_pur_sim_v1_multipart_materializes_exactly(tmp_path):
    encoded = ROOT / "data" / "pur_sim_v1" / "candidates_full.csv.xz.b64"
    out = tmp_path / "candidates_full.csv"
    got = materialize_pur_sim_v1(out, encoded)
    assert hashlib.sha256(got.read_bytes()).hexdigest() == EXPECTED_CANDIDATE_SHA256
    df = pd.read_csv(got)
    assert df.shape == (928, 14)
    assert df["source_candidate_id"].nunique() == 928
    assert df["blend"].nunique() == 58
    for cid in ("WO_INV_0419", "WO_INV_0420", "WO_INV_0579"):
        assert (df["source_candidate_id"] == cid).sum() == 1
